"""renamed state DB column to manual_state

Revision ID: 1001716f9e55
Revises: bb669dd41b5f
Create Date: 2021-12-05 18:58:09.463015+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1001716f9e55'
down_revision = 'bb669dd41b5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('zones', sa.Column('manual_state', sa.String(), nullable=True))
    op.alter_column('zones', 'pin_num',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('zones', 'state')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('zones', sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.alter_column('zones', 'pin_num',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('zones', 'manual_state')
    # ### end Alembic commands ###