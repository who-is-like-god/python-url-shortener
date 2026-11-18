"""create urls table

Revision ID: 0edd5b92b880
Revises: 
Create Date: 2026-09-09 01:51:12.229606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0edd5b92b880'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    #pass
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("original_url", sa.String, nullable=False),
        sa.Column("short_code", sa.String(length=6), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_urls_short_code",
        "urls",
        ["short_code"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # pass
    op.drop_index("ix_urls_short_code", table_name="urls")
    op.drop_table("urls")