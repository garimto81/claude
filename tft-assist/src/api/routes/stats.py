"""Stats API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from src.api.deps import get_db
from src.db.models import AugmentScore, ChampionScore, Match, Player, TraitScore
from src.schemas.augment import AugmentScoreResponse
from src.schemas.champion import ChampionScoreResponse
from src.schemas.stats import StatsOverviewResponse
from src.schemas.trait import TraitScoreResponse

router = APIRouter()


@router.get("/overview", response_model=StatsOverviewResponse)
async def get_stats_overview(
    session: Session = Depends(get_db),
) -> StatsOverviewResponse:
    """Get statistics overview.

    Returns:
        Overview with counts and top items
    """
    # Get counts
    total_matches = session.exec(select(func.count()).select_from(Match)).one()
    total_players = session.exec(select(func.count()).select_from(Player)).one()
    total_augments = session.exec(select(func.count()).select_from(AugmentScore)).one()
    champ_count_query = select(func.count()).select_from(ChampionScore)
    total_champions = session.exec(champ_count_query).one()
    total_traits = session.exec(select(func.count()).select_from(TraitScore)).one()

    # Get top 5 augments
    top_augments_query = (
        select(AugmentScore).order_by(AugmentScore.weighted_score.desc()).limit(5)
    )
    top_augments_results = session.exec(top_augments_query).all()

    top_augments = [
        AugmentScoreResponse(
            augment_id=r.augment_id,
            name=r.name,
            score=r.weighted_score,
            pick_count=r.pick_count,
            avg_placement=r.avg_placement,
            win_rate=r.win_rate,
        )
        for r in top_augments_results
    ]

    # Get top 5 champions
    top_champions_query = (
        select(ChampionScore).order_by(ChampionScore.weighted_score.desc()).limit(5)
    )
    top_champions_results = session.exec(top_champions_query).all()

    top_champions = [
        ChampionScoreResponse(
            champion_id=r.champion_id,
            name=r.name,
            score=r.weighted_score,
            pick_count=r.pick_count,
            avg_placement=r.avg_placement,
            win_rate=r.win_rate,
        )
        for r in top_champions_results
    ]

    # Get top 5 traits
    top_traits_query = (
        select(TraitScore).order_by(TraitScore.weighted_score.desc()).limit(5)
    )
    top_traits_results = session.exec(top_traits_query).all()

    top_traits = [
        TraitScoreResponse(
            trait_id=r.trait_id,
            name=r.name,
            score=r.weighted_score,
            pick_count=r.pick_count,
            avg_placement=r.avg_placement,
            win_rate=r.win_rate,
            avg_tier=r.avg_tier,
        )
        for r in top_traits_results
    ]

    # Get last updated
    last_updated = session.exec(select(func.max(AugmentScore.updated_at))).first()

    return StatsOverviewResponse(
        total_matches=total_matches,
        total_players=total_players,
        total_augments=total_augments,
        total_champions=total_champions,
        total_traits=total_traits,
        top_augments=top_augments,
        top_champions=top_champions,
        top_traits=top_traits,
        last_updated=last_updated,
    )
