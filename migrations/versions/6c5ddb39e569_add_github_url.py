"""Add github_url

Revision ID: 6c5ddb39e569
Revises: ad9c31da2cdf
Create Date: 2022-12-02 17:02:06.909296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c5ddb39e569'
down_revision = 'ad9c31da2cdf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('github_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'github_url')
    # ### end Alembic commands ###
