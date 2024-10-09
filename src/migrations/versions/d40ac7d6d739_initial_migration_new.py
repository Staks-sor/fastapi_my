"""initial migration new

Revision ID: d40ac7d6d739
Revises: 6a87797bcdd9
Create Date: 2024-10-09 17:34:10.342444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd40ac7d6d739'
down_revision: Union[str, None] = '6a87797bcdd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('rooms',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('hotel_id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('rooms')
