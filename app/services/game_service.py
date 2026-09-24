from typing import Optional

from app.models.game import Platform
from app.repositories.game import GameRepository
from app.schemas.gamefly import GameCreate


class GameService:
    def __init__(self, game_repo: GameRepository):
        self.game_repo = game_repo

    def create_game(
        self,
        title: str,
        platform: str,
        genre: Optional[str] = None,
        rating: Optional[str] = None,
        boxart: Optional[str] = None,
    ):
        # Validate platform early so unit tests get a clear error.
        valid = {p.value for p in Platform}
        if platform not in valid:
            raise ValueError(f"Invalid platform '{platform}'. Expected one of {sorted(valid)}")
        return self.game_repo.create(
            GameCreate(
                title=title,
                platform=platform,  # type: ignore[arg-type]
                genre=genre,
                rating=rating,
                boxart=boxart,
            )
        )

    def list_games(self, platform: Optional[str] = None):
        if platform is not None:
            valid = {p.value for p in Platform}
            if platform not in valid:
                raise ValueError(
                    f"Invalid platform '{platform}'. Expected one of {sorted(valid)}"
                )
        return self.game_repo.list(platform=platform)
