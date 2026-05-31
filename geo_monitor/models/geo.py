from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geo_monitor.database import Base


class Geo(Base):
    __tablename__ = "geos"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ru")
    rss_feeds: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    news: Mapped[list["News"]] = relationship(back_populates="geo")
    reports: Mapped[list["Report"]] = relationship(back_populates="geo")