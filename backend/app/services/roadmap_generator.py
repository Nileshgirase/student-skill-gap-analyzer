import json
from pathlib import Path
from typing import Any
from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.roadmap_item import RoadmapItem
from app.models.required_skill import RequiredSkill
from app.services.skill_extractor import extract_skills_from_text
from app.services.gap_analyzer import compute_skill_gap_analysis

RESOURCES_FILE = Path(__file__).resolve().parent.parent / "resources" / "learning_resources.json"


def load_resource_catalog() -> dict[str, list[dict[str, Any]]]:
    """Loads the verified free learning resource catalog from disk."""
    if not RESOURCES_FILE.exists():
        return {}
    try:
        with open(RESOURCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def generate_roadmap_items(analysis: Analysis, db: Session) -> list[RoadmapItem]:
    """
    Generates a personalized, time-bounded learning roadmap based on verified skill gaps
    and the student's weekly study budget.

    Adheres strictly to system constraints:
    1. Highest priority to missing strictly required skills, then beginner skills.
    2. Sum of planned hours per week never exceeds weekly_hours budget.
    3. Plan expands across additional weeks rather than overloading.
    4. Only verified free resources are utilized; no fabricated links.
    5. Saves items to the database with 'not_started' status.
    """
    catalog = load_resource_catalog()

    # Ensure required_skills are extracted on snapshots before computing gaps
    needed_commit = False
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
            needed_commit = True

    if needed_commit:
        db.commit()
        db.refresh(analysis)

    gap_result = compute_skill_gap_analysis(analysis)

    # Filter gaps needing study: 'missing' or 'needs_improvement'
    actionable_gaps = [
        gap for gap in gap_result.skill_gaps
        if gap["status"] in ("missing", "needs_improvement")
    ]

    # Priority ranking function:
    # 1. Strictly required + missing (rank 1)
    # 2. Strictly required + needs_improvement (rank 2)
    # 3. Preferred + missing (rank 3)
    # 4. Preferred + needs_improvement (rank 4)
    # 5. Others (rank 5)
    def priority_key(g: dict) -> int:
        req = g["requirement_type"]
        status = g["status"]
        if req == "required" and status == "missing":
            return 1
        if req == "required" and status == "needs_improvement":
            return 2
        if req == "preferred" and status == "missing":
            return 3
        if req == "preferred" and status == "needs_improvement":
            return 4
        return 5

    actionable_gaps.sort(key=priority_key)

    weekly_budget = float(max(1, analysis.weekly_hours))
    current_week = 1
    current_week_hours = 0.0
    new_roadmap_items: list[RoadmapItem] = []

    for gap in actionable_gaps:
        canonical = gap["canonical_skill"]
        display_name = gap["display_name"]
        available_resources = catalog.get(canonical, [])

        if available_resources:
            # Schedule resources from the catalog
            for res in available_resources:
                hours = float(res.get("estimated_hours", 4.0))

                # If resource exceeds entire weekly budget, split or cap at budget
                allocated_hours = min(hours, weekly_budget)

                # Check if adding this task overflows current week's available budget
                if (current_week_hours + allocated_hours) > weekly_budget and current_week_hours > 0:
                    current_week += 1
                    current_week_hours = 0.0

                item = RoadmapItem(
                    analysis_id=analysis.id,
                    week_number=current_week,
                    skill_name=display_name,
                    canonical_skill=canonical,
                    learning_goal=res.get("learning_goal", f"Master core competencies in {display_name}."),
                    resource_title=res.get("title", f"{display_name} Free Learning Guide"),
                    resource_url=res.get("url", ""),
                    resource_provider=res.get("provider", "Free Open Courseware"),
                    estimated_hours=allocated_hours,
                    status="not_started",
                )
                new_roadmap_items.append(item)
                current_week_hours += allocated_hours

                if current_week_hours >= weekly_budget:
                    current_week += 1
                    current_week_hours = 0.0
        else:
            # Fallback for valid skills without pre-cataloged link (No fabricated URLs)
            allocated_hours = min(4.0, weekly_budget)
            if (current_week_hours + allocated_hours) > weekly_budget and current_week_hours > 0:
                current_week += 1
                current_week_hours = 0.0

            item = RoadmapItem(
                analysis_id=analysis.id,
                week_number=current_week,
                skill_name=display_name,
                canonical_skill=canonical,
                learning_goal=(
                    f"Study verified requirement '{display_name}'. Practice key concepts and "
                    f"build a practical mini-exercise demonstrating capability."
                ),
                resource_title=f"{display_name} Official Documentation & Community Tutorials",
                resource_url=f"https://www.google.com/search?q={canonical}+official+documentation+tutorial",
                resource_provider="Self-Directed Study",
                estimated_hours=allocated_hours,
                status="not_started",
            )
            new_roadmap_items.append(item)
            current_week_hours += allocated_hours

            if current_week_hours >= weekly_budget:
                current_week += 1
                current_week_hours = 0.0

    # Clear prior roadmap items for this analysis and persist new ones
    db.query(RoadmapItem).filter(RoadmapItem.analysis_id == analysis.id).delete()
    for item in new_roadmap_items:
        db.add(item)

    db.commit()
    for item in new_roadmap_items:
        db.refresh(item)

    return new_roadmap_items
