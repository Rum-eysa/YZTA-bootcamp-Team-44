"""Context Manager testleri (US-017)"""
import json
import uuid

import pytest
from app.models import EducationRecord, JobListing, Match, Project, User, WorkExperience
from app.services.context import (
    ContextManager,
    job_analysis_from_context,
    matching_gaps_from_context,
    user_profile_for_agents,
    user_profile_for_matching,
)


@pytest.mark.asyncio
async def test_context_manager_loads_user_and_listing(test_session):
    """ContextManager user ve listing yükleyebilmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context@example.com",
        hashed_password="x",
        skills=json.dumps(["Python", "FastAPI"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps(
            {
                "required_skills": ["Python", "FastAPI"],
                "nice_to_have_skills": ["Docker"],
                "seniority": "mid",
            }
        ),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(listing)

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    assert context["user"]["id"] == user_id
    assert context["user"]["email"] == "context@example.com"
    assert context["user"]["skills"] == ["Python", "FastAPI"]
    assert context["user"]["seniority"] == "mid"

    assert context["listing"]["id"] == listing_id
    assert context["listing"]["title"] == "Backend Developer"
    assert context["listing"]["required_skills"] == ["Python", "FastAPI"]
    assert context["listing"]["nice_to_have_skills"] == ["Docker"]


@pytest.mark.asyncio
async def test_context_manager_loads_match_if_exists(test_session):
    """ContextManager match verisini yükleyebilmeli (varsa)"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context2@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(listing)

    match = Match(
        user_id=user_id,
        listing_id=listing_id,
        score=85.0,
        matched_skills=json.dumps(["python"]),
        missing_skills=json.dumps([]),
        score_breakdown=json.dumps(
            {"required": 60.0, "nice_to_have": 5.0, "seniority": 20.0, "semantic_bonus": 0.0}
        ),
    )
    test_session.add(match)
    await test_session.commit()

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    assert context["match"] is not None
    assert context["match"]["score"] == 85.0
    assert context["match"]["matched_skills"] == ["python"]
    assert context["match"]["score_breakdown"]["required"] == 60.0


@pytest.mark.asyncio
async def test_context_manager_returns_none_for_match_if_not_exists(test_session):
    """ContextManager match yoksa None dönmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context3@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    assert context["match"] is None


@pytest.mark.asyncio
async def test_context_manager_loads_work_experiences(test_session):
    """ContextManager work experiences yükleyebilmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context4@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    exp1 = WorkExperience(
        user_id=user_id,
        company="Tech Corp",
        title="Senior Developer",
        description="Backend development",
    )
    exp2 = WorkExperience(
        user_id=user_id,
        company="Startup Inc",
        title="Junior Developer",
        description="Full stack development",
    )
    test_session.add_all([user, listing, exp1, exp2])
    await test_session.commit()

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    assert len(context["experiences"]) == 2
    assert context["experiences"][0]["company"] == "Tech Corp"
    assert context["experiences"][0]["title"] == "Senior Developer"
    assert context["experiences"][1]["company"] == "Startup Inc"
    assert context["experiences"][1]["title"] == "Junior Developer"


@pytest.mark.asyncio
async def test_context_manager_loads_education(test_session):
    """ContextManager eğitim kayıtlarını yükleyebilmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context-edu@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    edu1 = EducationRecord(
        user_id=user_id,
        school="ODTÜ",
        degree="Lisans",
        field_of_study="Bilgisayar Mühendisliği",
    )
    edu2 = EducationRecord(
        user_id=user_id,
        school="Lise",
        degree="Lise Diploması",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    test_session.add_all([edu1, edu2])
    await test_session.commit()

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    assert len(context["education"]) == 2
    schools = {edu["school"] for edu in context["education"]}
    assert schools == {"ODTÜ", "Lise"}


@pytest.mark.asyncio
async def test_context_manager_loads_projects(test_session):
    """ContextManager projects yükleyebilmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context5@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    proj1 = Project(
        user_id=user_id,
        title="E-commerce Platform",
        description="Full stack e-commerce",
        tech_stack=json.dumps(["React", "Node.js", "PostgreSQL"]),
        url="https://github.com/example/ecommerce",
    )
    proj2 = Project(
        user_id=user_id,
        title="API Gateway",
        description="Microservices gateway",
        tech_stack=json.dumps(["Python", "FastAPI", "Redis"]),
    )
    test_session.add(user)
    await test_session.flush()
    test_session.add(listing)
    await test_session.flush()
    test_session.add_all([proj1, proj2])
    await test_session.commit()

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    assert len(context["projects"]) == 2
    assert context["projects"][0]["title"] == "E-commerce Platform"
    assert context["projects"][0]["tech_stack"] == ["React", "Node.js", "PostgreSQL"]
    assert context["projects"][1]["title"] == "API Gateway"
    assert context["projects"][1]["tech_stack"] == ["Python", "FastAPI", "Redis"]


@pytest.mark.asyncio
async def test_context_helpers_build_agent_payloads(test_session):
    """Context helper'ları agent payload'larını doğru üretmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="helpers@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
        tone_preference="confident",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        company="Acme Corp",
        raw_text="a" * 60,
        parsed_json=json.dumps(
            {
                "required_skills": ["Python", "FastAPI"],
                "nice_to_have_skills": ["Docker"],
                "seniority": "mid",
                "position_title": "Backend Developer",
            }
        ),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()

    context = await ContextManager(test_session).load(user_id, listing_id)

    job_analysis = job_analysis_from_context(context)
    assert job_analysis["required_skills"] == ["Python", "FastAPI"]
    assert job_analysis["position_title"] == "Backend Developer"

    profile = user_profile_for_matching(context)
    assert profile["skills"] == ["Python"]
    assert profile["work_experiences"] == []

    agent_profile = user_profile_for_agents(context)
    assert agent_profile["skills"] == ["Python"]
    assert agent_profile["work_experiences"] == []
    assert agent_profile["projects"] == []
    assert agent_profile["education"] == []
    assert agent_profile["gender"] is None
    assert agent_profile["military_status"] is None

    gaps = matching_gaps_from_context(context)
    assert gaps == {}


@pytest.mark.asyncio
async def test_user_profile_for_agents_passes_through_personal_info_and_education(
    test_session,
):
    """Dolu kişisel bilgiler + eğitim, CV/önyazı ajanı profiline gerçekten geçmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="personal@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
        gender="Kadın",
        nationality="TC",
        driver_license="B",
        military_status="Muaf",
        birth_year=1997,
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()
    edu = EducationRecord(user_id=user_id, school="ODTÜ", degree="Lisans")
    test_session.add(edu)
    await test_session.commit()

    context = await ContextManager(test_session).load(user_id, listing_id)
    agent_profile = user_profile_for_agents(context)

    assert agent_profile["gender"] == "Kadın"
    assert agent_profile["nationality"] == "TC"
    assert agent_profile["driver_license"] == "B"
    assert agent_profile["military_status"] == "Muaf"
    assert agent_profile["birth_year"] == 1997
    assert len(agent_profile["education"]) == 1
    assert agent_profile["education"][0]["school"] == "ODTÜ"


@pytest.mark.asyncio
async def test_context_manager_raises_error_for_nonexistent_user(test_session):
    """ContextManager user bulunamazsa ValueError fırlatmalı"""
    listing_id = str(uuid.uuid4())

    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    test_session.add(listing)
    await test_session.commit()

    context_manager = ContextManager(test_session)
    with pytest.raises(ValueError, match="User not found"):
        await context_manager.load(str(uuid.uuid4()), listing_id)


@pytest.mark.asyncio
async def test_context_manager_raises_error_for_nonexistent_listing(test_session):
    """ContextManager listing bulunamazsa ValueError fırlatmalı"""
    user_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context6@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    test_session.add(user)
    await test_session.commit()

    context_manager = ContextManager(test_session)
    with pytest.raises(ValueError, match="Listing not found"):
        await context_manager.load(user_id, str(uuid.uuid4()))


@pytest.mark.asyncio
async def test_context_manager_returns_json_serializable_context(test_session):
    """ContextManager JSON serializable context dönmeli"""
    user_id = str(uuid.uuid4())
    listing_id = str(uuid.uuid4())

    user = User(
        id=user_id,
        email="context7@example.com",
        hashed_password="x",
        skills=json.dumps(["Python"]),
        seniority="mid",
    )
    listing = JobListing(
        id=listing_id,
        title="Backend Developer",
        raw_text="a" * 60,
        parsed_json=json.dumps({"required_skills": ["Python"], "seniority": "mid"}),
        analysis_status="completed",
    )
    test_session.add_all([user, listing])
    await test_session.commit()

    context_manager = ContextManager(test_session)
    context = await context_manager.load(user_id, listing_id)

    # JSON serializable testi
    json_str = json.dumps(context)
    assert json_str is not None
    assert len(json_str) > 0
