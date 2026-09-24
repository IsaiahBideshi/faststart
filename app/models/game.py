from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Platform(str, Enum):
    NSW = "NSW"
    PS5 = "PS5"
    XBOX = "XBOX"
    PC = "PC"


class GameBase(SQLModel):
    title: str
    platform: str = Field(index=True)
    genre: Optional[str] = Field(default=None)
    rating: Optional[str] = Field(default=None)
    boxart: Optional[str] = Field(default=None)


class Game(GameBase, table=True):
    gameId: Optional[int] = Field(default=None, primary_key=True)

    def toJSON(self) -> dict:
        return {
            "gameId": self.gameId,
            "title": self.title,
            "rating": self.rating,
            "platform": self.platform,
            "boxart": self.boxart,
            "genre": self.genre,
        }
