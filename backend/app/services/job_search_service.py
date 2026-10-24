from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.job_snapshot import JobSnapshot
from app.connectors.greenhouse import GreenhouseConnector


def execute_job_search(
    analysis: Analysis,
    db: Session,
    connector: GreenhouseConnector | None = None,
) -> tuple[str, str, list[JobSnapshot]]:
    """
    Executes live job retrieval across verified connectors, records snapshot provenance,
    and updates the analysis status according to system rules.
    """
    if connector is None:
        connector = GreenhouseConnector()

    status_code, message, normalized_jobs = connector.search_jobs_detailed(
        company_name=analysis.company_name,
        target_role=analysis.target_role,
    )

    created_snapshots: list[JobSnapshot] = []

    if status_code == "verified_jobs_found":
        # Replace previous snapshots for this analysis to ensure freshness
        db.query(JobSnapshot).filter(JobSnapshot.analysis_id == analysis.id).delete()

        for job in normalized_jobs:
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
                is_stale=job.is_stale,
                verification_status=job.verification_status,
                verification_notes=job.verification_notes,
            )
            db.add(snapshot)
            created_snapshots.append(snapshot)

        analysis.status = "verified_jobs_found"
    else:
        # If no verified postings or error, update analysis status explicitly
        analysis.status = status_code

    db.commit()
    for s in created_snapshots:
        db.refresh(s)

    return status_code, message, created_snapshots
