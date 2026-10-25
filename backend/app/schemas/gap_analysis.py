from pydantic import BaseModel, ConfigDict


class SkillGapItemSchema(BaseModel):
    canonical_skill: str
    display_name: str
    requirement_type: str
    student_proficiency: str
    status: str
    evidence_text: str | None = None
    source_employer: str | None = None
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class AdditionalSkillSchema(BaseModel):
    canonical_skill: str
    display_name: str
    proficiency_level: str
    status: str
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class GapAnalysisResponse(BaseModel):
    analysis_id: int
    company_name: str
    target_role: str
    total_jobs_analyzed: int
    coverage_percentage: float | None
    coverage_explanation: str
    unique_required_count: int
    covered_required_count: int
    missing_required_count: int
    needs_improvement_count: int
    skill_gaps: list[SkillGapItemSchema]
    additional_skills: list[AdditionalSkillSchema]

    model_config = ConfigDict(from_attributes=True)
