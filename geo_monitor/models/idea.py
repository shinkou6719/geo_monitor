from datetime import datetime
from typing import Optional
from sqlalchemy import Text, String, SmallInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geo_monitor.database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"))
    angle: Mapped[str] = mapped_column(Text, nullable=False)
    offer_connection: Mapped[Optional[str]] = mapped_column(Text)
    audience_pain: Mapped[Optional[str]] = mapped_column(Text)
    creative_type: Mapped[Optional[str]] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(5), default="C")
    freshness_days: Mapped[Optional[int]] = mapped_column(SmallInteger)
    trigger_strength: Mapped[Optional[int]] = mapped_column(SmallInteger)
    offer_match: Mapped[Optional[int]] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    news: Mapped["News"] = relationship(back_populates="ideas")
    headlines: Mapped[list["Headline"]] = relationship(back_populates="idea")