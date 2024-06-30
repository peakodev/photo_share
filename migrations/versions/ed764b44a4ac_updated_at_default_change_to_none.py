"""updated_at default change to None

Revision ID: ed764b44a4ac
Revises: f7c950df3777
Create Date: 2024-06-30 14:00:48.201274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed764b44a4ac'
down_revision: Union[str, None] = 'f7c950df3777'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.alter_column('posts', 'updated_at',
               existing_type=sa.DateTime(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'),
               server_default=None)

def downgrade():
    op.alter_column('posts', 'updated_at',
               existing_type=sa.DateTime(),
               nullable=False,
               existing_server_default=None,
               server_default=sa.text('CURRENT_TIMESTAMP'))
    