from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    original_url = Column(
        String,
        nullable=False
    )

    short_code = Column(
        String(10),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    click_count = Column(
        Integer,
        default=0,
        nullable=False
    )