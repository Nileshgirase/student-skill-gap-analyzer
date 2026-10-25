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
from app.schemas.job import JobSearchResponse
from app.schemas.gap_analysis import GapAnalysisResponse
from app.security.dependencies import get_current_user
from app.services.skill_normalizer import canonicalize_skill_name
from app.services.job_search_service import execute_job_search
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
    return analysis


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

    return JobSearchResponse(
        status=status_code,
        company=analysis.company_name,
        target_role=analysis.target_role,
        message=message,
        jobs=snapshots,
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
