"""extend brand model to text

Revision ID: 0d3ceb5bfb12
Revises: a66a6b45a9a6
Create Date: 2026-04-14 11:30:32.370149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d3ceb5bfb12'
down_revision: Union[str, None] = 'a66a6b45a9a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('cars', 'brand', type_=sa.Text(), existing_type=sa.String(100))
    op.alter_column('cars', 'model', type_=sa.Text(), existing_type=sa.String(100))


def downgrade() -> None:
    op.alter_column('cars', 'brand', type_=sa.String(100), existing_type=sa.Text())
    op.alter_column('cars', 'model', type_=sa.String(100), existing_type=sa.Text())
