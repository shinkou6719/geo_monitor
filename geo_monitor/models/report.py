from datetime import datetime
from typing import Optional
from sqlalchemy import SmallInteger, BigInteger, JSON, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geo_monitor.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    geo_id: Mapped[int] = mapped_column(ForeignKey("geos.id", ondelete="CASCADE"))
    period_from: Mapped[datetime]
    period_to: Mapped[datetime]
    total_news: Mapped[int] = mapped_column(SmallInteger, default=0)
    total_ideas: Mapped[int] = mapped_column(SmallInteger, default=0)
    total_headlines: Mapped[int] = mapped_column(SmallInteger, default=0)
    top_ideas: Mapped[list] = mapped_column(JSON, default=list)
    urgent_list: Mapped[list] = mapped_column(JSON, default=list)
    evergreen_list: Mapped[list] = mapped_column(JSON, default=list)
    telegram_msg_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="draft")

    geo: Mapped["Geo"] = relationship(back_populates="reports")