"""recreate tags

Revision ID: bab8b1d33bb2
Revises: ae3348d1cde2
Create Date: 2022-11-28 19:04:54.119118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bab8b1d33bb2'
down_revision = 'ae3348d1cde2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tagging',
    sa.Column('project_id', sa.String(), nullable=False),
    sa.Column('tag_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['tag_name'], ['tag.name'], )
    )
    op.drop_table('taggings')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('taggings',
    sa.Column('project_id', sa.INTEGER(), nullable=False),
    sa.Column('tag_name', sa.VARCHAR(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['tag_name'], ['tag.name'], )
    )
    op.drop_table('tagging')
    # ### end Alembic commands ###