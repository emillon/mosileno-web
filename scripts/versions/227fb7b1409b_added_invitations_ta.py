"""Added invitations table

Revision ID: 227fb7b1409b
Revises: None
Create Date: 2012-11-22 23:51:39.625473

"""

# revision identifiers, used by Alembic.
revision = '227fb7b1409b'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invitations')
    ### end Alembic commands ###