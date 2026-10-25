from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.analysis import Analysis
from app.models.roadmap_item import RoadmapItem
from app.schemas.roadmap import (
    RoadmapResponse,
    RoadmapItemResponse,
    RoadmapUpdateStatusRequest,
)
from app.security.dependencies import get_current_user
from app.services.roadmap_generator import generate_roadmap_items

router = APIRouter(tags=["Roadmaps"])


@router.get(
    "/api/analyses/{analysis_id}/roadmap",
    response_model=RoadmapResponse,
    summary="Get Analysis Roadmap",
    description="Returns the personalized, week-by-week learning roadmap for the student's owned analysis.",
)
def get_roadmap(
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

    items = (
        db.query(RoadmapItem)
        .filter(RoadmapItem.analysis_id == analysis.id)
        .order_by(RoadmapItem.week_number.asc(), RoadmapItem.id.asc())
        .all()
    )

    total_weeks = max([item.week_number for item in items], default=0)
    total_hours = sum([item.estimated_hours for item in items], 0.0)

    return RoadmapResponse(
        analysis_id=analysis.id,
        company_name=analysis.company_name,
        target_role=analysis.target_role,
        weekly_hours_budget=analysis.weekly_hours,
        total_weeks=total_weeks,
        total_estimated_hours=round(total_hours, 1),
        items=items,
    )


@router.post(
    "/api/analyses/{analysis_id}/roadmap",
    response_model=RoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate or Re-generate Personalized Learning Roadmap",
    description=(
        "Synthesizes verified skill gaps with curated free learning resources and schedules "
        "tasks week-by-week strictly bounded by the student's study availability."
    ),
)
def create_roadmap(
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
            detail="Cannot generate roadmap without verified job postings. Please run job search first.",
        )

    items = generate_roadmap_items(analysis=analysis, db=db)

    total_weeks = max([item.week_number for item in items], default=0)
    total_hours = sum([item.estimated_hours for item in items], 0.0)

    return RoadmapResponse(
        analysis_id=analysis.id,
        company_name=analysis.company_name,
        target_role=analysis.target_role,
        weekly_hours_budget=analysis.weekly_hours,
        total_weeks=total_weeks,
        total_estimated_hours=round(total_hours, 1),
        items=items,
    )


@router.patch(
    "/api/roadmap-items/{item_id}",
    response_model=RoadmapItemResponse,
    summary="Update Roadmap Item Progress",
    description="Updates the progress status ('not_started', 'in_progress', 'completed') of an owned roadmap task.",
)
def update_roadmap_item_status(
    item_id: int,
    payload: RoadmapUpdateStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify ownership through the parent analysis
    item = (
        db.query(RoadmapItem)
        .join(Analysis)
        .filter(RoadmapItem.id == item_id, Analysis.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap item not found or you do not have permission to modify it.",
        )

    item.status = payload.status
    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item
