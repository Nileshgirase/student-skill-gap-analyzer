from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.models.student_skill import StudentSkill
from app.models.required_skill import RequiredSkill
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisSummaryResponse,
    AnalysisDetailResponse,
    StudentSkillsUpdateRequest,
    SkillResponseSchema,
)
from app.schemas.job import JobSearchResponse, UserProvidedJobRequest
from app.schemas.gap_analysis import GapAnalysisResponse
from app.security.dependencies import get_current_user
from app.services.skill_normalizer import canonicalize_skill_name
from app.services.job_search_service import (
    execute_job_search,
    find_cached_snapshots,
    apply_cached_snapshot_to_analysis,
    create_user_provided_snapshot,
)
from app.services.skill_extractor import extract_skills_from_text
from app.services.gap_analyzer import compute_skill_gap_analysis

router = APIRouter(prefix="/api/analyses", tags=["Analyses"])


@router.post(
    "",
    response_model=AnalysisDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Skill Gap Analysis",
    description=(
        "Initiates a new skill gap analysis for a free-text company name and target role, "
        "saving the student's study hour commitment and self-reported skills."
    ),
)
def create_analysis(
    payload: AnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = Analysis(
        user_id=current_user.id,
        company_name=payload.company_name,
        target_role=payload.target_role,
        weekly_hours=payload.weekly_hours,
        status="pending",
    )
    db.add(analysis)
    db.flush()  # Populates analysis.id for foreign keys

    # Deduplicate skills by canonical key within the same analysis
    seen_canonical: set[str] = set()
    for skill_input in payload.student_skills:
        canonical = canonicalize_skill_name(skill_input.name)
        if canonical not in seen_canonical:
            seen_canonical.add(canonical)
            skill = StudentSkill(
                analysis_id=analysis.id,
                skill_name=skill_input.name,
                canonical_skill=canonical,
                proficiency_level=skill_input.proficiency,
                self_reported=True,
            )
            db.add(skill)

    db.commit()
    db.refresh(analysis)
    return analysis


@router.get(
    "",
    response_model=list[AnalysisSummaryResponse],
    summary="List Student Analyses",
    description="Returns the authenticated student's analysis history, ordered from newest to oldest.",
)
def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    summaries = []
    for item in analyses:
        summaries.append(
            AnalysisSummaryResponse(
                id=item.id,
                company_name=item.company_name,
                target_role=item.target_role,
                weekly_hours=item.weekly_hours,
                status=item.status,
                skill_count=len(item.student_skills),
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        )
    return summaries


@router.get(
    "/{analysis_id}",
    response_model=AnalysisDetailResponse,
    summary="Get Analysis by ID",
    description="Fetches a single analysis owned by the current student, including reported skills.",
)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    response_data = AnalysisDetailResponse.model_validate(analysis)
    if not analysis.job_snapshots:
        cached_matches = find_cached_snapshots(
            company_name=analysis.company_name,
            target_role=analysis.target_role,
            db=db,
            exclude_analysis_id=analysis.id,
        )
        if cached_matches:
            response_data.has_cached_snapshots = True
            response_data.cached_snapshot_title = cached_matches[0]["job_title"]
            response_data.cached_snapshot_date = cached_matches[0]["fetched_at"]

    return response_data


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Analysis",
    description="Deletes an owned analysis and cascade-removes associated student skills.",
)
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    db.delete(analysis)
    db.commit()
    return None


@router.post(
    "/{analysis_id}/student-skills",
    response_model=list[SkillResponseSchema],
    summary="Update or Replace Student Skills",
    description="Replaces the student skill entries for an owned analysis with an updated set.",
)
def update_student_skills(
    analysis_id: int,
    payload: StudentSkillsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    # Delete existing skills for this analysis
    db.query(StudentSkill).filter(StudentSkill.analysis_id == analysis.id).delete()

    # Add updated skills
    seen_canonical: set[str] = set()
    new_skills = []
    for skill_input in payload.student_skills:
        canonical = canonicalize_skill_name(skill_input.name)
        if canonical not in seen_canonical:
            seen_canonical.add(canonical)
            skill = StudentSkill(
                analysis_id=analysis.id,
                skill_name=skill_input.name,
                canonical_skill=canonical,
                proficiency_level=skill_input.proficiency,
                self_reported=True,
            )
            db.add(skill)
            new_skills.append(skill)

    db.commit()
    for s in new_skills:
        db.refresh(s)

    return new_skills


@router.post(
    "/{analysis_id}/search-jobs",
    response_model=JobSearchResponse,
    summary="Search Permitted Sources for Verified Jobs",
    description=(
        "Executes live retrieval against permitted source connectors for the target company and role. "
        "Deduplicates results, records source evidence, and updates the analysis verification status."
    ),
)
def search_jobs_for_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    status_code, message, snapshots = execute_job_search(analysis=analysis, db=db)

    has_cached = False
    cached_count = 0
    cached_title = None
    cached_date = None
    cached_emp = None

    if not snapshots:
        cached_matches = find_cached_snapshots(
            company_name=analysis.company_name,
            target_role=analysis.target_role,
            db=db,
            exclude_analysis_id=analysis.id,
        )
        if cached_matches:
            has_cached = True
            cached_count = len(cached_matches)
            cached_title = cached_matches[0]["job_title"]
            cached_date = cached_matches[0]["fetched_at"]
            cached_emp = cached_matches[0]["employer_name"]

    return JobSearchResponse(
        status=status_code,
        company=analysis.company_name,
        target_role=analysis.target_role,
        message=message,
        jobs=snapshots,
        has_cached_snapshots=has_cached,
        cached_snapshot_count=cached_count,
        cached_snapshot_title=cached_title,
        cached_snapshot_date=cached_date,
        cached_snapshot_employer=cached_emp,
    )


@router.post(
    "/{analysis_id}/use-cached-posting",
    response_model=JobSearchResponse,
    summary="Use Last Known / Cached Job Posting",
    description=(
        "Attaches the most recent verified historical posting for the target company and role "
        "when live career feeds have no open positions. Marks the posting as an archived snapshot."
    ),
)
def use_cached_posting(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    snapshots = apply_cached_snapshot_to_analysis(analysis=analysis, db=db)
    if not snapshots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No verified historical or cached postings found for '{analysis.company_name}' "
                f"matching '{analysis.target_role}'."
            ),
        )

    return JobSearchResponse(
        status="archived_jobs_found",
        company=analysis.company_name,
        target_role=analysis.target_role,
        message=f"Attached last known verified posting: '{snapshots[0].job_title}' ({snapshots[0].source_name}).",
        jobs=snapshots,
        has_cached_snapshots=False,
    )


@router.post(
    "/{analysis_id}/paste-job-description",
    response_model=JobSearchResponse,
    summary="Provide Job Description Directly",
    description=(
        "Attaches a job description provided directly by the student (e.g. copied from a company's "
        "career page, LinkedIn, or job board) for companies without public ATS feeds."
    ),
)
def paste_job_description(
    analysis_id: int,
    payload: UserProvidedJobRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    snapshot = create_user_provided_snapshot(
        analysis=analysis,
        db=db,
        description_text=payload.description_text,
        job_title=payload.job_title,
        source_url=payload.source_url,
    )

    return JobSearchResponse(
        status="verified_jobs_found",
        company=analysis.company_name,
        target_role=analysis.target_role,
        message=f"Attached student-provided job description for '{snapshot.job_title}'.",
        jobs=[snapshot],
        has_cached_snapshots=False,
    )


@router.post(
    "/{analysis_id}/run-gap-analysis",
    response_model=GapAnalysisResponse,
    summary="Execute Evidence-Backed Skill Gap Analysis",
    description=(
        "Extracts required skills from verified job snapshots, compares them against "
        "student-reported proficiency, computes coverage metrics, and catalogs gaps."
    ),
)
def run_gap_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    if not analysis.job_snapshots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No verified job postings found for this analysis. "
                "Please run job search successfully before analyzing skill gaps."
            ),
        )

    # Extract skills for any snapshot that doesn't yet have required_skills populated
    for snapshot in analysis.job_snapshots:
        if not snapshot.required_skills:
            extracted_items = extract_skills_from_text(snapshot.description_text)
            for item in extracted_items:
                req_skill = RequiredSkill(
                    job_snapshot_id=snapshot.id,
                    skill_name=item.skill_name,
                    canonical_skill=item.canonical_skill,
                    requirement_type=item.requirement_type,
                    evidence_text=item.evidence_text,
                    extraction_method=item.extraction_method,
                    confidence=item.confidence,
                )
                db.add(req_skill)

    db.commit()
    db.refresh(analysis)

    # Compute skill gap comparisons and coverage metric
    result = compute_skill_gap_analysis(analysis)

    # Update status to analysis_complete
    analysis.status = "analysis_complete"
    db.commit()

    return result
