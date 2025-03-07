"""Auto-update migration

Revision ID: 778d852eb0be
Revises: 
Create Date: 2025-02-13 00:48:41.556498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '778d852eb0be'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('explanation_versions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('scale_name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('examples', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_explanation_versions_id'), 'explanation_versions', ['id'], unique=False)
    op.create_index(op.f('ix_explanation_versions_scale_name'), 'explanation_versions', ['scale_name'], unique=False)
    op.create_index(op.f('ix_explanation_versions_version_number'), 'explanation_versions', ['version_number'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_explanation_versions_version_number'), table_name='explanation_versions')
    op.drop_index(op.f('ix_explanation_versions_scale_name'), table_name='explanation_versions')
    op.drop_index(op.f('ix_explanation_versions_id'), table_name='explanation_versions')
    op.drop_table('explanation_versions')
    # ### end Alembic commands ###
