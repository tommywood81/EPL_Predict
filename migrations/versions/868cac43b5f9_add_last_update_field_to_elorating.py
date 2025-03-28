"""Add last_update field to EloRating

Revision ID: 868cac43b5f9
Revises: bd0c6bf22536
Create Date: 2025-03-26 17:25:28.240414

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '868cac43b5f9'
down_revision = 'bd0c6bf22536'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('elo_ratings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_update', sa.DateTime(), nullable=True))
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('elo_ratings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.drop_column('last_update')

    # ### end Alembic commands ###
