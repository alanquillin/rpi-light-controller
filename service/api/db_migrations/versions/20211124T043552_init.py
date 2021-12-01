"""init

Revision ID: bb669dd41b5f
Revises: 
Create Date: 2021-11-24 04:35:52.888298+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb669dd41b5f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('zones',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('program', sa.String(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.Column('pin_num', sa.Integer(), nullable=False),
    sa.Column('on', sa.String(), nullable=False),
    sa.Column('off', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('zones')
    # ### end Alembic commands ###
