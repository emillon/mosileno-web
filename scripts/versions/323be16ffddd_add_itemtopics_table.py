"""Add itemtopics table

Revision ID: 323be16ffddd
Revises: 6a172eccde1
Create Date: 2012-11-29 21:19:35.766645

"""

# revision identifiers, used by Alembic.
revision = '323be16ffddd'
down_revision = '6a172eccde1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('itemtopics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item', sa.Integer(), nullable=True),
    sa.Column('topic', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['item'], ['items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table(u'kombu_message')
    op.drop_table(u'celery_taskmeta')
    op.drop_table(u'kombu_queue')
    op.drop_table(u'sqlite_sequence')
    op.drop_table(u'celery_tasksetmeta')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'celery_tasksetmeta',
    sa.Column(u'id', sa.INTEGER(), nullable=False),
    sa.Column(u'taskset_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column(u'result', sa.BLOB(), nullable=True),
    sa.Column(u'date_done', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.create_table(u'sqlite_sequence',
    sa.Column(u'name', sa.VARCHAR(), nullable=True),
    sa.Column(u'seq', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint()
    )
    op.create_table(u'kombu_queue',
    sa.Column(u'id', sa.INTEGER(), nullable=False),
    sa.Column(u'name', sa.VARCHAR(length=200), nullable=True),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.create_table(u'celery_taskmeta',
    sa.Column(u'id', sa.INTEGER(), nullable=False),
    sa.Column(u'task_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column(u'status', sa.VARCHAR(length=50), nullable=True),
    sa.Column(u'result', sa.BLOB(), nullable=True),
    sa.Column(u'date_done', sa.DATETIME(), nullable=True),
    sa.Column(u'traceback', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.create_table(u'kombu_message',
    sa.Column(u'id', sa.INTEGER(), nullable=False),
    sa.Column(u'visible', sa.BOOLEAN(), nullable=True),
    sa.Column(u'timestamp', sa.DATETIME(), nullable=True),
    sa.Column(u'payload', sa.TEXT(), nullable=False),
    sa.Column(u'queue_id', sa.INTEGER(), nullable=True),
    sa.Column(u'version', sa.SMALLINT(), nullable=False),
    sa.ForeignKeyConstraint(['queue_id'], [u'kombu_queue.id'], ),
    sa.PrimaryKeyConstraint(u'id')
    )
    op.drop_table('itemtopics')
    ### end Alembic commands ###