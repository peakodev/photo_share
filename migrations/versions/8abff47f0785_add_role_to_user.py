"""add role to user

Revision ID: 8abff47f0785
Revises: d6a0d78dc4cc
Create Date: 2024-06-24 16:03:37.643706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8abff47f0785'
down_revision: Union[str, None] = 'd6a0d78dc4cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = postgresql.ENUM('user', 'admin', 'moderator', name='role')


def upgrade() -> None:
    # Create the enum type in the database
    role_enum.create(op.get_bind(), checkfirst=True)

    # Add the column with the new enum type and default value
    op.add_column('users', sa.Column('role', role_enum, nullable=True, server_default='user'))

    # Manually update all existing records to have the default role 'user'
    op.execute("UPDATE users SET role = 'user'")

    # Alter the column to make it non-nullable
    op.alter_column('users', 'role', nullable=False, server_default=None)


def downgrade() -> None:
    # Remove the column
    op.drop_column('users', 'role')

    # Drop the enum type from the database
    role_enum.drop(op.get_bind(), checkfirst=True)
