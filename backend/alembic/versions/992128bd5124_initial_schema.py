from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "992128bd5124"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "person",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("department", sa.Text(), nullable=False),
        sa.Column("job_title", sa.Text(), nullable=False),
        sa.Column("identity", sa.Integer(), nullable=False),
        sa.Column("specialize_classify", sa.Integer(), nullable=False),
        sa.Column("education", sa.Text(), nullable=True),
        sa.Column("gender", sa.Integer(), nullable=False),
        sa.Column("production_group_classify", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_person_name", "person", ["name"])
    op.create_index("idx_person_department", "person", ["department"])
    op.create_index("idx_person_identity", "person", ["identity"])
    op.create_index(
        "idx_person_specialize_classify",
        "person",
        ["specialize_classify"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_person_specialize_classify",
        table_name="person",
    )
    op.drop_index(
        "idx_person_identity",
        table_name="person",
    )
    op.drop_index(
        "idx_person_department",
        table_name="person",
    )
    op.drop_index(
        "idx_person_name",
        table_name="person",
    )

    op.drop_table("person")