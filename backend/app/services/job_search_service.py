import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from app.config import settings
from app.models.analysis import Analysis
from app.models.job_snapshot import JobSnapshot
from app.connectors.base import BaseJobConnector, NormalizedJob
from app.connectors.greenhouse import GreenhouseConnector, calculate_role_relevance
from app.connectors.lever import LeverConnector

logger = logging.getLogger(__name__)

ARCHIVED_CATALOG_PATH = Path(__file__).resolve().parent.parent / "resources" / "archived_job_snapshots.json"


def get_archived_catalog() -> list[dict]:
    """Loads the curated catalog of verified historical job postings."""
    if not ARCHIVED_CATALOG_PATH.exists():
        return []
    try:
        with open(ARCHIVED_CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed to load archived job catalog: %s", exc)
        return []


def normalize_company_for_lookup(name: str) -> str:
    """Normalizes company names and maps common enterprise aliases."""
    cleaned = re.sub(r"[^a-z0-9]", "", name.lower())
    aliases = {
        "hcl": "hcltech",
        "hcltech": "hcltech",
        "hcltechnologies": "hcltech",
        "tcs": "tcs",
        "tataconsultancy": "tcs",
        "tataconsultancyservices": "tcs",
        "wipro": "wipro",
        "wiprotechnologies": "wipro",
        "cognizant": "cognizant",
        "cts": "cognizant",
        "accenture": "accenture",
        "infosys": "infosys",
        "infy": "infosys",
        "google": "google",
        "alphabet": "google",
        "microsoft": "microsoft",
        "msft": "microsoft",
        "amazon": "amazon",
        "aws": "amazon",
        "meta": "meta",
        "facebook": "meta",
        "stripe": "stripe",
    }
    return aliases.get(cleaned, cleaned)


def find_cached_snapshots(
    company_name: str,
    target_role: str,
    db: Session,
    exclude_analysis_id: int | None = None,
) -> list[dict]:
    """
    Finds historical or cached job snapshots matching the company name and target role.
    Checks:
    1. Existing verified snapshots stored in the local SQLite database.
    2. Curated catalog of verified historical postings in archived_job_snapshots.json.
    Returns matched postings sorted by fetch date descending.
    """
    matches: list[dict] = []
    clean_company = company_name.strip().lower()
    norm_company = normalize_company_for_lookup(company_name)

    # 1. Check local SQLite DB
    query = db.query(JobSnapshot).filter(
        JobSnapshot.verification_status.in_(["verified", "archived_snapshot"])
    )
    if exclude_analysis_id:
        query = query.filter(JobSnapshot.analysis_id != exclude_analysis_id)

    db_snapshots = query.order_by(JobSnapshot.fetched_at.desc()).all()
    for snap in db_snapshots:
        snap_emp = snap.employer_name.strip().lower()
        snap_norm = normalize_company_for_lookup(snap.employer_name)
        if clean_company in snap_emp or snap_emp in clean_company or norm_company == snap_norm:
            is_rel, _ = calculate_role_relevance(snap.job_title, target_role)
            if is_rel:
                matches.append({
                    "source": "database_cache",
                    "employer_name": snap.employer_name,
                    "job_title": snap.job_title,
                    "source_name": snap.source_name,
                    "source_url": snap.source_url,
                    "source_type": snap.source_type,
                    "location": snap.location,
                    "employment_type": snap.employment_type,
                    "description_text": snap.description_text,
                    "posted_at": snap.posted_at,
                    "fetched_at": snap.fetched_at,
                    "content_hash": snap.content_hash,
                })

    # 2. Check archived catalog if no DB match or to supplement
    catalog = get_archived_catalog()
    for item in catalog:
        cat_emp = item.get("employer_name", "").strip().lower()
        cat_norm = normalize_company_for_lookup(item.get("employer_name", ""))
        if clean_company in cat_emp or cat_emp in clean_company or norm_company == cat_norm:
            is_rel, _ = calculate_role_relevance(item.get("job_title", ""), target_role)
            if is_rel:
                if not any(
                    normalize_company_for_lookup(m["employer_name"]) == cat_norm and m["job_title"].lower() == item.get("job_title", "").lower()
                    for m in matches
                ):
                    posted = None
                    if item.get("posted_at"):
                        try:
                            posted = datetime.fromisoformat(item["posted_at"])
                        except Exception:
                            posted = None
                    fetched = datetime.now(timezone.utc)
                    if item.get("fetched_at"):
                        try:
                            fetched = datetime.fromisoformat(item["fetched_at"])
                        except Exception:
                            fetched = datetime.now(timezone.utc)

                    matches.append({
                        "source": "archived_catalog",
                        "employer_name": item["employer_name"],
                        "job_title": item["job_title"],
                        "source_name": item["source_name"],
                        "source_url": item["source_url"],
                        "source_type": item.get("source_type", "archived_posting"),
                        "location": item.get("location"),
                        "employment_type": item.get("employment_type"),
                        "description_text": item["description_text"],
                        "posted_at": posted,
                        "fetched_at": fetched,
                        "content_hash": None,
                    })

    return matches


def create_user_provided_snapshot(
    analysis: Analysis,
    db: Session,
    description_text: str,
    job_title: str | None = None,
    source_url: str | None = None,
) -> JobSnapshot:
    """
    Creates and attaches a user-provided job posting snapshot (e.g. pasted directly
    from a company's career page, LinkedIn, or job board).
    Extracts real requirements using sentence-level text evidence.
    """
    # Remove existing snapshots
    db.query(JobSnapshot).filter(JobSnapshot.analysis_id == analysis.id).delete()

    effective_title = (job_title or analysis.target_role).strip()
    effective_url = (
        source_url.strip()
        if source_url and source_url.strip()
        else f"https://careers.google.com/search?q={analysis.company_name}"
    )

    snapshot = JobSnapshot(
        analysis_id=analysis.id,
        source_name=f"{analysis.company_name} Career Posting",
        source_url=effective_url,
        source_type="user_provided_posting",
        employer_name=analysis.company_name,
        job_title=effective_title,
        location="Provided by Student",
        employment_type="Full-time",
        description_text=description_text.strip(),
        fetched_at=datetime.now(timezone.utc),
        posted_at=datetime.now(timezone.utc),
        is_stale=False,
        verification_status="user_verified",
        verification_notes="Job description provided directly by student. Requirements extracted with sentence-level text evidence.",
    )
    db.add(snapshot)
    analysis.status = "verified_jobs_found"
    db.commit()
    db.refresh(snapshot)
    return snapshot


def apply_cached_snapshot_to_analysis(
    analysis: Analysis,
    db: Session,
    cached_match: dict | None = None,
) -> list[JobSnapshot]:
    """
    Attaches a historical or cached job posting to an analysis, marking it explicitly
    as an archived snapshot with freshness warning notes.
    """
    if cached_match is None:
        matches = find_cached_snapshots(
            company_name=analysis.company_name,
            target_role=analysis.target_role,
            db=db,
            exclude_analysis_id=analysis.id,
        )
        if not matches:
            return []
        cached_match = matches[0]

    # Remove any existing snapshots and skills for this analysis
    db.query(JobSnapshot).filter(JobSnapshot.analysis_id == analysis.id).delete()

    orig_date = (
        cached_match["fetched_at"].strftime("%Y-%m-%d")
        if isinstance(cached_match.get("fetched_at"), datetime)
        else "past posting"
    )

    archived_note = (
        f"Archived snapshot loaded from last verified posting on {orig_date}. "
        "This requisition was previously verified from public career sources but may no longer be actively hiring."
    )

    snapshot = JobSnapshot(
        analysis_id=analysis.id,
        source_name=cached_match["source_name"],
        source_url=cached_match["source_url"],
        source_type="archived_snapshot",
        employer_name=cached_match["employer_name"],
        job_title=cached_match["job_title"],
        location=cached_match.get("location"),
        employment_type=cached_match.get("employment_type"),
        description_text=cached_match["description_text"],
        fetched_at=datetime.now(timezone.utc),
        posted_at=cached_match.get("posted_at"),
        content_hash=cached_match.get("content_hash"),
        is_stale=True,
        verification_status="archived_snapshot",
        verification_notes=archived_note,
    )
    db.add(snapshot)
    analysis.status = "archived_jobs_found"
    db.commit()
    db.refresh(snapshot)
    return [snapshot]


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
