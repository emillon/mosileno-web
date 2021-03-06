"""Add usertopicnames table

Revision ID: 195912da2e1d
Revises: cd7de59a304
Create Date: 2012-11-30 09:47:21.016038

"""

# revision identifiers, used by Alembic.
revision = '195912da2e1d'
down_revision = 'cd7de59a304'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usertopicnames',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=True),
    sa.Column('topicname', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['user'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usertopicnames')
    ### end Alembic commands ###
