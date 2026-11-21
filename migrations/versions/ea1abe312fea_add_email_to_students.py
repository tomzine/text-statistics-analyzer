"""add email to students

Revision ID: ea1abe312fea
Revises: e29171cc01e7
Create Date: 2026-11-18 16:27:20.165540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea1abe312fea'
down_revision: Union[str, Sequence[str], None] = 'e29171cc01e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    with op.batch_alter_table(
        "students",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "email",
                sa.String(length=150),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            "uq_students_email",
            ["email"]
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table(
        "students",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "uq_students_email",
            type_="unique"
        )

        batch_op.drop_column("email")


    # ### end Alembic commands ###
