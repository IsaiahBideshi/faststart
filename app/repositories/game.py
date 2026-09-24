import logging
from typing import Optional

from sqlmodel import Session, select

from app.models.game import Game
from app.schemas.gamefly import GameCreate

logger = logging.getLogger(__name__)


class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: GameCreate) -> Game:
        game = Game(
            title=data.title,
            platform=data.platform.value if hasattr(data.platform, "value") else str(data.platform),
            genre=data.genre,
            rating=data.rating,
            boxart=data.boxart,
        )
        try:
            self.db.add(game)
            self.db.commit()
            self.db.refresh(game)
            return game
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            self.db.rollback()
            raise

    def get_by_id(self, game_id: int) -> Optional[Game]:
        return self.db.get(Game, game_id)

    def list(self, platform: Optional[str] = None) -> list[Game]:
        q = select(Game)
        if platform:
            q = q.where(Game.platform == platform)
        return list(self.db.exec(q).all())
