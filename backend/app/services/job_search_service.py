import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.config import settings
from app.models.analysis import Analysis
from app.models.job_snapshot import JobSnapshot
from app.connectors.base import BaseJobConnector, NormalizedJob
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector

logger = logging.getLogger(__name__)


def get_default_connectors() -> list[BaseJobConnector]:
    """Returns the ordered list of supported, permitted ATS source connectors."""
    return [
        GreenhouseConnector(),
        LeverConnector(),
    ]


def evaluate_posting_freshness(posted_at: datetime | None) -> tuple[bool, str | None]:
    """
    Evaluates whether a job posting is stale based on the configured freshness threshold.
    Returns (is_stale, note).
    """
    if posted_at is None:
        return False, None

    now = datetime.now(timezone.utc)
    # Ensure posted_at is timezone-aware
    if posted_at.tzinfo is None:
        posted_at = posted_at.replace(tzinfo=timezone.utc)

    age_days = (now - posted_at).days
    if age_days > settings.job_freshness_days:
        return True, f"Posting is {age_days} days old (exceeds freshness policy of {settings.job_freshness_days} days)."
    return False, f"Fresh posting ({age_days} days old)."


def execute_job_search(
    analysis: Analysis,
    db: Session,
    connectors: list[BaseJobConnector] | None = None,
) -> tuple[str, str, list[JobSnapshot]]:
    """
    Queries multiple permitted source connectors in order of priority,
    merges and deduplicates results, enforces freshness tracking,
    and updates analysis status.
    """
    if connectors is None:
        connectors = get_default_connectors()

    all_normalized_jobs: list[NormalizedJob] = []
    connector_statuses: dict[str, str] = {}
    successful_sources: list[str] = []

    for conn in connectors:
        source_name = getattr(conn, "source_name", conn.__class__.__name__)
        try:
            if hasattr(conn, "search_jobs_detailed"):
                status_code, msg, jobs = conn.search_jobs_detailed(
                    company_name=analysis.company_name,
                    target_role=analysis.target_role,
                )
            else:
                jobs = conn.search_jobs(
                    company_name=analysis.company_name,
                    target_role=analysis.target_role,
                )
                status_code = "verified_jobs_found" if jobs else "no_matching_jobs"

            connector_statuses[source_name] = status_code
            if jobs:
                all_normalized_jobs.extend(jobs)
                successful_sources.append(source_name)
        except Exception as exc:
            logger.warning("Connector %s failed for %s: %s", source_name, analysis.company_name, str(exc))
            connector_statuses[source_name] = "source_unavailable"

    # Deduplicate postings across connectors using content_hash and source_url
    deduped_jobs: list[NormalizedJob] = []
    seen_hashes: set[str] = set()
    seen_urls: set[str] = set()

    for job in all_normalized_jobs:
        url_key = job.source_url.strip().lower()
        hash_key = job.content_hash or ""

        if url_key in seen_urls:
            continue
        if hash_key and hash_key in seen_hashes:
            continue

        seen_urls.add(url_key)
        if hash_key:
            seen_hashes.add(hash_key)
        deduped_jobs.append(job)

    created_snapshots: list[JobSnapshot] = []

    if deduped_jobs:
        # Clear prior snapshots for this analysis to keep results current
        db.query(JobSnapshot).filter(JobSnapshot.analysis_id == analysis.id).delete()

        for job in deduped_jobs:
            # Check freshness policy
            is_stale, freshness_note = evaluate_posting_freshness(job.posted_at)

            # Combine verification notes with freshness note
            notes_parts = [job.verification_notes] if job.verification_notes else []
            if freshness_note:
                notes_parts.append(freshness_note)
            combined_notes = " | ".join(notes_parts) if notes_parts else None

            snapshot = JobSnapshot(
                analysis_id=analysis.id,
                source_name=job.source_name,
                source_url=job.source_url,
                source_type=job.source_type,
                employer_name=job.employer_name,
                job_title=job.job_title,
                location=job.location,
                employment_type=job.employment_type,
                description_text=job.description_text,
                fetched_at=job.fetched_at,
                posted_at=job.posted_at,
                content_hash=job.content_hash,
                is_stale=is_stale,
                verification_status=job.verification_status,
                verification_notes=combined_notes,
            )
            db.add(snapshot)
            created_snapshots.append(snapshot)

        final_status = "verified_jobs_found"
        sources_str = ", ".join(sorted(set(successful_sources)))
        message = f"Found {len(created_snapshots)} verified job posting(s) across {sources_str}."
        analysis.status = final_status
    else:
        # Determine aggregate fallback status
        statuses = list(connector_statuses.values())
        if all(s == "source_unavailable" for s in statuses):
            final_status = "source_unavailable"
            message = "All permitted job source connectors were unreachable or timed out."
        elif any(s == "no_matching_jobs" for s in statuses):
            final_status = "no_matching_jobs"
            message = (
                f"Public job board was verified for {analysis.company_name}, "
                f"but no open postings matched target role '{analysis.target_role}'."
            )
        else:
            final_status = "company_not_verified"
            message = f"Could not verify public job boards for '{analysis.company_name}' on supported sources."

        analysis.status = final_status

    db.commit()
    for s in created_snapshots:
        db.refresh(s)

    return final_status, message, created_snapshots
