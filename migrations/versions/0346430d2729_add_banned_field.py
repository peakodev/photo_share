"""add banned field

Revision ID: 0346430d2729
Revises: 8abff47f0785
Create Date: 2024-06-28 08:33:57.802692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0346430d2729'
down_revision: Union[str, None] = '8abff47f0785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the column as nullable
    op.add_column('users', sa.Column('banned', sa.Boolean(), nullable=True))

    # Step 2: Update the table to set a default value for existing rows
    op.execute('UPDATE users SET banned = False')  # Assuming False is the desired default

    # Step 3: Alter the column to NOT NULL
    op.alter_column('users', 'banned', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'banned')
