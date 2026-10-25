from dataclasses import dataclass, asdict
from typing import Literal

from app.models.analysis import Analysis
from app.models.student_skill import StudentSkill
from app.models.required_skill import RequiredSkill

GapStatus = Literal[
    "self_reported_covered",
    "needs_improvement",
    "missing",
    "additional_skill",
    "uncertain_requirement",
]


@dataclass
class SkillGapItem:
    canonical_skill: str
    display_name: str
    requirement_type: str  # required, preferred, mentioned, uncertain
    student_proficiency: str  # beginner, intermediate, advanced, none
    status: GapStatus
    evidence_text: str | None
    source_employer: str | None
    explanation: str


@dataclass
class GapAnalysisResult:
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
    skill_gaps: list[dict]
    additional_skills: list[dict]


def compute_skill_gap_analysis(analysis: Analysis) -> GapAnalysisResult:
    """
    Compares verified required skills extracted from job snapshots against
    the student's self-reported skills to produce an explainable skill gap comparison
    and a mathematically grounded coverage metric.
    """
    student_skills_map: dict[str, StudentSkill] = {
        s.canonical_skill: s for s in analysis.student_skills
    }

    # Gather all extracted required skills across snapshots, deduplicating by canonical_skill
    # If a skill appears across multiple postings, select the strongest requirement type
    all_req_skills: list[RequiredSkill] = []
    total_snapshots = len(analysis.job_snapshots)

    for snapshot in analysis.job_snapshots:
        all_req_skills.extend(snapshot.required_skills)

    unique_req_map: dict[str, RequiredSkill] = {}
    for r in all_req_skills:
        canonical = r.canonical_skill
        if canonical not in unique_req_map:
            unique_req_map[canonical] = r
        else:
            # Prefer 'required' over 'preferred' or 'mentioned'
            if r.requirement_type == "required":
                unique_req_map[canonical] = r

    skill_gaps: list[SkillGapItem] = []
    covered_required_count = 0
    missing_required_count = 0
    needs_improvement_count = 0
    total_required_skills = 0

    for canonical, req in unique_req_map.items():
        is_strictly_required = req.requirement_type == "required"
        if is_strictly_required:
            total_required_skills += 1

        student_skill = student_skills_map.get(canonical)
        student_prof = student_skill.proficiency_level if student_skill else "none"

        employer = req.job_snapshot.employer_name if req.job_snapshot else analysis.company_name

        if req.requirement_type == "uncertain":
            gap_item = SkillGapItem(
                canonical_skill=canonical,
                display_name=req.skill_name,
                requirement_type=req.requirement_type,
                student_proficiency=student_prof,
                status="uncertain_requirement",
                evidence_text=req.evidence_text,
                source_employer=employer,
                explanation="Job description mentions this skill, but context is ambiguous as to necessity.",
            )
        elif not student_skill:
            gap_item = SkillGapItem(
                canonical_skill=canonical,
                display_name=req.skill_name,
                requirement_type=req.requirement_type,
                student_proficiency="none",
                status="missing",
                evidence_text=req.evidence_text,
                source_employer=employer,
                explanation="Employer specified this requirement, but student did not report it (not proof of inability).",
            )
            if is_strictly_required:
                missing_required_count += 1
        elif student_prof == "beginner":
            gap_item = SkillGapItem(
                canonical_skill=canonical,
                display_name=req.skill_name,
                requirement_type=req.requirement_type,
                student_proficiency=student_prof,
                status="needs_improvement",
                evidence_text=req.evidence_text,
                source_employer=employer,
                explanation="Student reported beginner proficiency; target role expects proven competency.",
            )
            if is_strictly_required:
                needs_improvement_count += 1
        else:  # intermediate or advanced
            gap_item = SkillGapItem(
                canonical_skill=canonical,
                display_name=req.skill_name,
                requirement_type=req.requirement_type,
                student_proficiency=student_prof,
                status="self_reported_covered",
                evidence_text=req.evidence_text,
                source_employer=employer,
                explanation="Self-reported coverage based on student input (not independent verification).",
            )
            if is_strictly_required:
                covered_required_count += 1

        skill_gaps.append(gap_item)

    # Calculate coverage score
    if total_required_skills == 0:
        coverage_percentage = None
        coverage_explanation = (
            "Not enough verified required skills extracted from job postings to calculate a numerical coverage score. "
            "Review mentioned and preferred skills below."
        )
    else:
        coverage_percentage = round((covered_required_count / total_required_skills) * 100, 1)
        coverage_explanation = (
            f"Self-reported coverage is {coverage_percentage}% ({covered_required_count} of {total_required_skills} "
            f"strictly required skills covered). Note: This is an explanatory estimate based on student self-assessment, "
            f"not an employment guarantee or hiring probability."
        )

    # Identify additional student skills not in job requirements
    additional_skills = []
    for canonical, student_skill in student_skills_map.items():
        if canonical not in unique_req_map:
            additional_skills.append({
                "canonical_skill": canonical,
                "display_name": student_skill.skill_name,
                "proficiency_level": student_skill.proficiency_level,
                "status": "additional_skill",
                "explanation": "Student reported this skill, but it was not explicitly required in verified job postings.",
            })

    return GapAnalysisResult(
        analysis_id=analysis.id,
        company_name=analysis.company_name,
        target_role=analysis.target_role,
        total_jobs_analyzed=total_snapshots,
        coverage_percentage=coverage_percentage,
        coverage_explanation=coverage_explanation,
        unique_required_count=total_required_skills,
        covered_required_count=covered_required_count,
        missing_required_count=missing_required_count,
        needs_improvement_count=needs_improvement_count,
        skill_gaps=[asdict(g) for g in skill_gaps],
        additional_skills=additional_skills,
    )
