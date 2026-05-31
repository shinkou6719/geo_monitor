from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, SmallInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geo_monitor.database import Base


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    geo_id: Mapped[int] = mapped_column(ForeignKey("geos.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(50), default="rss")
    published_at: Mapped[Optional[datetime]]
    fetched_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    raw_content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    emotional_trigger: Mapped[Optional[str]] = mapped_column(String(50))
    urgency: Mapped[str] = mapped_column(String(20), default="week")
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_score: Mapped[Optional[int]] = mapped_column(SmallInteger)

    geo: Mapped["Geo"] = relationship(back_populates="news")
    ideas: Mapped[list["Idea"]] = relationship(back_populates="news")