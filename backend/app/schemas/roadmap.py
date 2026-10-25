from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

ItemStatus = Literal["not_started", "in_progress", "completed"]


class RoadmapItemResponse(BaseModel):
    id: int
    analysis_id: int
    week_number: int
    skill_name: str
    canonical_skill: str
    learning_goal: str
    resource_title: str
    resource_url: str
    resource_provider: str
    estimated_hours: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoadmapUpdateStatusRequest(BaseModel):
    status: ItemStatus = Field(
        ...,
        description="Updated status: 'not_started', 'in_progress', or 'completed'",
    )


class RoadmapResponse(BaseModel):
    analysis_id: int
    company_name: str
    target_role: str
    weekly_hours_budget: int
    total_weeks: int
    total_estimated_hours: float
    items: list[RoadmapItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
