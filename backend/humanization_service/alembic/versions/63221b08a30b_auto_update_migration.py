"""Auto-update migration

Revision ID: 63221b08a30b
Revises: 7ace8a9bcfb1
Create Date: 2025-02-07 21:32:07.641529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63221b08a30b'
down_revision: Union[str, None] = '7ace8a9bcfb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
