from datetime import datetime
from typing import Optional

from sqlalchemy import Text, String, ForeignKey, Computed
from sqlalchemy.orm import Mapped, mapped_column, relationship

from geo_monitor.database import Base


class Headline(Base):
    __tablename__ = "headlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    idea_id: Mapped[int] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[Optional[str]] = mapped_column(String(30))
    char_count: Mapped[int] = mapped_column(Computed("length(text)"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    idea: Mapped["Idea"] = relationship(back_populates="headlines")