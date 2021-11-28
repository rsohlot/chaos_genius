"""dashboard and dashboard_kpi_mapper

Revision ID: f7d137e094dd
Revises: f5f55452fa58
Create Date: 2021-11-23 08:40:55.497857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7d137e094dd'
down_revision = 'f5f55452fa58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dashboard',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('last_modified', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dashboard_kpi_mapper',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dashboard', sa.Integer(), nullable=False),
    sa.Column('kpi', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboard_kpi_mapper_dashboard'), 'dashboard_kpi_mapper', ['dashboard'], unique=False)
    op.create_index(op.f('ix_dashboard_kpi_mapper_kpi'), 'dashboard_kpi_mapper', ['kpi'], unique=False)
    op.drop_table('data_upload')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_upload',
    sa.Column('c1', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c2', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c3', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c4', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c5', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c6', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c7', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c8', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c9', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c10', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('c11', sa.TEXT(), autoincrement=False, nullable=True)
    )
    op.drop_index(op.f('ix_dashboard_kpi_mapper_kpi'), table_name='dashboard_kpi_mapper')
    op.drop_index(op.f('ix_dashboard_kpi_mapper_dashboard'), table_name='dashboard_kpi_mapper')
    op.drop_table('dashboard_kpi_mapper')
    op.drop_table('dashboard')
    # ### end Alembic commands ###
