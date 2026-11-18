from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(6),
        unique=True,
        index=True,
        nullable=False,
    )

    visit_count: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
        nullable=False,
    )