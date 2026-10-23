"""Odwiedzający wersję demonstracyjną (bramka „przedstaw się”). Celowo bez IP i user-agenta."""
import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .enums import utcnow


class DemoVisitor(Base):
    """Imię, nazwisko i firma osoby, która weszła do demo; kasowane po 90 dniach."""
    __tablename__ = "demo_visitors"
    __table_args__ = (Index("ix_demo_visitors_created_at", "created_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    company: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=utcnow)
