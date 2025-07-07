from __future__ import annotations

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ChannelSheet(Base):
    """Mapping of channel names to spreadsheet IDs."""

    __tablename__ = "channel_sheet"  # type: ignore[assignment]

    __table_args__ = (
        UniqueConstraint("organisation_id", "channel", name="uq_org_channel"),
    )

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    folder_id: Mapped[str] = mapped_column(String(128), nullable=False)
    spreadsheet_id: Mapped[str] = mapped_column(String(128), nullable=False)
