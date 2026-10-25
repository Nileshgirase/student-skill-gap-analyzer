from datetime import datetime, timezone
from app.models.analysis import Analysis
from app.models.student_skill import StudentSkill
from app.models.job_snapshot import JobSnapshot
from app.models.required_skill import RequiredSkill
from app.models.roadmap_item import RoadmapItem
from app.services.roadmap_generator import generate_roadmap_items


def test_roadmap_prioritization_and_weekly_budget(db_session):
    """
    Verifies that:
    1. Strictly required missing skills are prioritized before beginner or preferred skills.
    2. Sum of planned hours for each week NEVER exceeds the weekly_hours budget.
    3. The plan expands across multiple weeks.
    """
    now = datetime.now(timezone.utc)
    # Student has 6 hours of weekly study budget
    analysis = Analysis(
        user_id=1,
        company_name="Stripe",
        target_role="Backend Engineer",
        weekly_hours=6,
        status="verified_jobs_found",
    )
    db_session.add(analysis)
    db_session.flush()

    # Student skills: beginner in Docker
    student_docker = StudentSkill(
        analysis_id=analysis.id,
        skill_name="Docker",
        canonical_skill="docker",
        proficiency_level="beginner",
    )
    db_session.add(student_docker)

    snapshot = JobSnapshot(
        analysis_id=analysis.id,
        source_name="Greenhouse",
        source_url="https://boards.greenhouse.io/stripe/jobs/1",
        source_type="public_ats_feed",
        employer_name="Stripe",
        job_title="Backend Engineer",
        description_text="Job description",
        fetched_at=now,
        verification_status="verified",
    )
    db_session.add(snapshot)
    db_session.flush()

    # Requirements:
    # 1. Python: required & missing (Priority 1)
    # 2. Docker: required & beginner (Priority 2)
    # 3. GraphQL: preferred & missing (Priority 3)
    reqs = [
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="GraphQL", canonical_skill="graphql", requirement_type="preferred", evidence_text="GraphQL a plus."),
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="Python", canonical_skill="python", requirement_type="required", evidence_text="Python required."),
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="Docker", canonical_skill="docker", requirement_type="required", evidence_text="Docker required."),
    ]
    db_session.add_all(reqs)
    db_session.commit()
    db_session.refresh(analysis)

    items = generate_roadmap_items(analysis=analysis, db=db_session)
    assert len(items) >= 3

    # Check prioritization: Python must appear in Week 1 before Docker / GraphQL
    python_items = [it for it in items if it.canonical_skill == "python"]
    docker_items = [it for it in items if it.canonical_skill == "docker"]
    graphql_items = [it for it in items if it.canonical_skill == "graphql"]

    assert python_items[0].week_number <= docker_items[0].week_number
    assert docker_items[0].week_number <= graphql_items[0].week_number

    # Verify weekly budget rule: no single week can exceed weekly_hours (6 hours)
    hours_per_week: dict[int, float] = {}
    for it in items:
        hours_per_week[it.week_number] = hours_per_week.get(it.week_number, 0.0) + it.estimated_hours

    for week_num, total_h in hours_per_week.items():
        assert total_h <= 6.0, f"Week {week_num} exceeded 6-hour budget with {total_h} hours"

    # Plan must span more than 1 week
    assert max(hours_per_week.keys()) > 1


def test_roadmap_catalog_resource_provenance(db_session):
    """Verifies that all generated tasks use verified free resources with valid titles and providers."""
    now = datetime.now(timezone.utc)
    analysis = Analysis(user_id=1, company_name="Corp", target_role="Dev", weekly_hours=10, status="verified_jobs_found")
    db_session.add(analysis)
    db_session.flush()

    snapshot = JobSnapshot(
        analysis_id=analysis.id,
        source_name="Lever",
        source_url="https://jobs.lever.co/corp/1",
        source_type="public_ats_feed",
        employer_name="Corp",
        job_title="Dev",
        description_text="Text",
        fetched_at=now,
        verification_status="verified",
    )
    db_session.add(snapshot)
    db_session.flush()

    req = RequiredSkill(
        job_snapshot_id=snapshot.id,
        skill_name="PostgreSQL",
        canonical_skill="postgresql",
        requirement_type="required",
        evidence_text="PostgreSQL required.",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(analysis)

    items = generate_roadmap_items(analysis=analysis, db=db_session)
    assert len(items) >= 1
    for it in items:
        assert it.resource_url.startswith("http")
        assert len(it.resource_title) > 0
        assert len(it.resource_provider) > 0
        assert it.status == "not_started"


def test_api_create_and_get_roadmap_integration(client, db_session):
    """
    Integration test verifying:
    POST /api/analyses/{id}/roadmap
    GET /api/analyses/{id}/roadmap
    """
    # 1. Register student
    reg = client.post(
        "/api/auth/register",
        json={"name": "Roadmap User", "email": "roadmap.user@example.com", "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 2. Create analysis
    analysis_res = client.post(
        "/api/analyses",
        json={"company_name": "GitHub", "target_role": "Software Engineer", "weekly_hours": 8},
        headers=headers,
    )
    analysis_id = analysis_res.json()["id"]

    # 3. Add verified job snapshot directly to DB
    now = datetime.now(timezone.utc)
    snapshot = JobSnapshot(
        analysis_id=analysis_id,
        source_name="Greenhouse",
        source_url="https://boards.greenhouse.io/github/1",
        source_type="public_ats_feed",
        employer_name="GitHub",
        job_title="Software Engineer",
        description_text="Requirements:\n• Experience with Python and Git required.\n",
        fetched_at=now,
        verification_status="verified",
    )
    db_session.add(snapshot)
    db_session.commit()

    # 4. Create roadmap
    post_res = client.post(f"/api/analyses/{analysis_id}/roadmap", headers=headers)
    assert post_res.status_code == 201
    post_data = post_res.json()
    assert post_data["analysis_id"] == analysis_id
    assert post_data["weekly_hours_budget"] == 8
    assert len(post_data["items"]) >= 2
    assert post_data["total_weeks"] >= 1

    # 5. Get roadmap
    get_res = client.get(f"/api/analyses/{analysis_id}/roadmap", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert len(get_data["items"]) == len(post_data["items"])


def test_api_patch_roadmap_item_progress_and_ownership(client, db_session):
    """
    Verifies that:
    1. A student can update progress via PATCH /api/roadmap-items/{id}.
    2. Other students cannot update another user's roadmap item.
    """
    # Register User A
    reg_a = client.post(
        "/api/auth/register",
        json={"name": "User A", "email": "user.a.roadmap@example.com", "password": "Password123!"},
    )
    headers_a = {"Authorization": f"Bearer {reg_a.json()['access_token']}"}

    # Register User B
    reg_b = client.post(
        "/api/auth/register",
        json={"name": "User B", "email": "user.b.roadmap@example.com", "password": "Password123!"},
    )
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    # User A creates analysis and roadmap item
    analysis_res = client.post(
        "/api/analyses",
        json={"company_name": "Amazon", "target_role": "Engineer", "weekly_hours": 10},
        headers=headers_a,
    )
    analysis_id = analysis_res.json()["id"]

    now = datetime.now(timezone.utc)
    item = RoadmapItem(
        analysis_id=analysis_id,
        week_number=1,
        skill_name="Python",
        canonical_skill="python",
        learning_goal="Complete Python tutorial",
        resource_title="Python Docs",
        resource_url="https://docs.python.org",
        resource_provider="PSF",
        estimated_hours=5.0,
        status="not_started",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    item_id = item.id

    # User B attempts to patch User A's roadmap item -> 404
    bad_patch = client.patch(
        f"/api/roadmap-items/{item_id}",
        json={"status": "completed"},
        headers=headers_b,
    )
    assert bad_patch.status_code == 404

    # User A patches to 'in_progress'
    patch_1 = client.patch(
        f"/api/roadmap-items/{item_id}",
        json={"status": "in_progress"},
        headers=headers_a,
    )
    assert patch_1.status_code == 200
    assert patch_1.json()["status"] == "in_progress"

    # User A patches to 'completed'
    patch_2 = client.patch(
        f"/api/roadmap-items/{item_id}",
        json={"status": "completed"},
        headers=headers_a,
    )
    assert patch_2.status_code == 200
    assert patch_2.json()["status"] == "completed"

    # Verify persistence in database
    db_item = db_session.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
    assert db_item.status == "completed"


def test_create_roadmap_without_snapshots_fails_400(client):
    """Verifies that attempting to create a roadmap without verified job postings fails with 400."""
    reg = client.post(
        "/api/auth/register",
        json={"name": "No Snapshot User", "email": "no.snapshots.roadmap@example.com", "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    analysis_res = client.post(
        "/api/analyses",
        json={"company_name": "Figma", "target_role": "Designer", "weekly_hours": 10},
        headers=headers,
    )
    analysis_id = analysis_res.json()["id"]

    res = client.post(f"/api/analyses/{analysis_id}/roadmap", headers=headers)
    assert res.status_code == 400
    assert "without verified job postings" in res.json()["detail"].lower()
