"""Integration tests for API endpoints."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.api.main import app
from src.api.deps import get_db

# Import all models to ensure they are registered with SQLModel metadata
from src.db.models import (
    AugmentScore,
    ChampionScore,
    Match,
    MatchAugment,
    MatchChampion,
    MatchPlayer,
    Player,
    TraitScore,
)


@pytest.fixture(scope="function")
def test_engine():
    """Create in-memory SQLite engine with thread-safe settings."""
    # Use StaticPool to share connection across sessions (required for in-memory SQLite)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create database session."""
    with Session(test_engine) as session:
        yield session


def create_sample_data(session: Session):
    """Create sample data for testing."""
    now = datetime.now(timezone.utc)

    # Create players
    player = Player(
        puuid="test-puuid",
        summoner_id="s1",
        summoner_name="TestPlayer",
        league_points=1500,
        rank_position=1,
        created_at=now,
        updated_at=now,
    )
    session.add(player)

    # Create matches
    for i in range(5):
        match = Match(
            match_id=f"KR_{i}",
            game_datetime=now,
            game_length=1800.0,
            game_version="14.1",
            created_at=now,
        )
        session.add(match)

    # Create augment scores
    augments = [
        ("TFT_Augment_A", "Augment A", 9.5, 100, 1.5, 40.0),
        ("TFT_Augment_B", "Augment B", 8.0, 80, 2.5, 25.0),
        ("TFT_Augment_C", "Augment C", 6.5, 60, 3.5, 15.0),
    ]
    for aug_id, name, score, picks, avg, win in augments:
        aug = AugmentScore(
            augment_id=aug_id,
            name=name,
            pick_count=picks,
            total_games=picks,
            weighted_score=score,
            avg_placement=avg,
            win_rate=win,
            updated_at=now,
        )
        session.add(aug)

    # Create champion scores
    champions = [
        ("TFT_Jinx", "Jinx", 9.0, 150, 1.8, 35.0),
        ("TFT_Vi", "Vi", 7.5, 120, 2.8, 20.0),
    ]
    for champ_id, name, score, picks, avg, win in champions:
        champ = ChampionScore(
            champion_id=champ_id,
            name=name,
            pick_count=picks,
            total_games=picks,
            weighted_score=score,
            avg_placement=avg,
            win_rate=win,
            updated_at=now,
        )
        session.add(champ)

    # Create trait scores
    traits = [
        ("Set16_Brawler", "Brawler", 9.2, 200, 1.6, 38.0, 2.5),
        ("Set16_Sniper", "Sniper", 7.8, 150, 2.5, 22.0, 2.0),
        ("Set16_Academy", "Academy", 6.0, 100, 3.2, 12.0, 1.8),
    ]
    for trait_id, name, score, picks, avg, win, avg_tier in traits:
        trait = TraitScore(
            trait_id=trait_id,
            name=name,
            pick_count=picks,
            total_games=picks,
            weighted_score=score,
            avg_placement=avg,
            win_rate=win,
            avg_tier=avg_tier,
            updated_at=now,
        )
        session.add(trait)

    session.commit()


@pytest.fixture(scope="function")
def client_with_data(test_engine, test_session):
    """Create test client with sample data."""
    # Ensure tables exist
    SQLModel.metadata.create_all(test_engine)
    create_sample_data(test_session)

    def override_get_db():
        with Session(test_engine) as s:
            yield s

    app.dependency_overrides[get_db] = override_get_db

    # Use raise_server_exceptions=False to skip lifespan events in test
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_empty(test_engine):
    """Create test client without data."""
    # Ensure tables exist
    SQLModel.metadata.create_all(test_engine)

    def override_get_db():
        with Session(test_engine) as s:
            yield s

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, client_empty):
        """Health check should return ok status."""
        response = client_empty.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAugmentsEndpoint:
    """Tests for augments endpoints."""

    def test_get_all_augments(self, client_with_data):
        """Should return all augment scores."""
        response = client_with_data.get("/api/augments")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

        # Should be sorted by score descending
        scores = [item["score"] for item in data["items"]]
        assert scores == sorted(scores, reverse=True)

    def test_get_augments_with_pagination(self, client_with_data):
        """Should support pagination."""
        response = client_with_data.get("/api/augments?limit=2&offset=0")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3

    def test_get_augment_detail(self, client_with_data):
        """Should return specific augment details."""
        response = client_with_data.get("/api/augments/TFT_Augment_A")
        assert response.status_code == 200

        data = response.json()
        assert data["augment_id"] == "TFT_Augment_A"
        assert data["name"] == "Augment A"
        assert data["score"] == 9.5
        assert data["tier"] == "S+"

    def test_get_augment_not_found(self, client_with_data):
        """Should return 404 for unknown augment."""
        response = client_with_data.get("/api/augments/unknown")
        assert response.status_code == 404

    def test_get_augments_by_tier(self, client_with_data):
        """Should filter augments by tier."""
        response = client_with_data.get("/api/augments/tier/S+")
        assert response.status_code == 200

        data = response.json()
        # Only Augment A has score >= 8.5
        assert len(data["items"]) == 1
        assert data["items"][0]["tier"] == "S+"


class TestChampionsEndpoint:
    """Tests for champions endpoints."""

    def test_get_all_champions(self, client_with_data):
        """Should return all champion scores."""
        response = client_with_data.get("/api/champions")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_champion_detail(self, client_with_data):
        """Should return specific champion details."""
        response = client_with_data.get("/api/champions/TFT_Jinx")
        assert response.status_code == 200

        data = response.json()
        assert data["champion_id"] == "TFT_Jinx"
        assert data["name"] == "Jinx"
        assert data["tier"] == "S+"


class TestStatsEndpoint:
    """Tests for stats endpoints."""

    def test_get_stats_overview(self, client_with_data):
        """Should return statistics overview."""
        response = client_with_data.get("/api/stats/overview")
        assert response.status_code == 200

        data = response.json()
        assert data["total_matches"] == 5
        assert data["total_players"] == 1
        assert data["total_augments"] == 3
        assert data["total_champions"] == 2
        assert data["total_traits"] == 3
        assert len(data["top_augments"]) <= 5
        assert len(data["top_champions"]) <= 5
        assert len(data["top_traits"]) <= 5


class TestTraitsEndpoint:
    """Tests for traits endpoints."""

    def test_get_all_traits(self, client_with_data):
        """Should return all trait scores."""
        response = client_with_data.get("/api/traits")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

        # Should be sorted by score descending
        scores = [item["score"] for item in data["items"]]
        assert scores == sorted(scores, reverse=True)

    def test_get_traits_with_pagination(self, client_with_data):
        """Should support pagination."""
        response = client_with_data.get("/api/traits?limit=2&offset=0")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3

    def test_get_trait_detail(self, client_with_data):
        """Should return specific trait details."""
        response = client_with_data.get("/api/traits/Set16_Brawler")
        assert response.status_code == 200

        data = response.json()
        assert data["trait_id"] == "Set16_Brawler"
        assert data["name"] == "Brawler"
        assert data["score"] == 9.2
        assert data["tier"] == "S+"
        assert data["avg_tier"] == 2.5

    def test_get_trait_not_found(self, client_with_data):
        """Should return 404 for unknown trait."""
        response = client_with_data.get("/api/traits/unknown")
        assert response.status_code == 404

    def test_get_traits_by_tier(self, client_with_data):
        """Should filter traits by tier."""
        response = client_with_data.get("/api/traits/tier/S+")
        assert response.status_code == 200

        data = response.json()
        # Only Brawler has score >= 8.5
        assert len(data["items"]) == 1
        assert data["items"][0]["tier"] == "S+"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root(self, client_empty):
        """Root should return API info."""
        response = client_empty.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "TFT Overlay Guide API"
        assert "version" in data
