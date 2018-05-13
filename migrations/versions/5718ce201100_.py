"""empty message

Revision ID: 5718ce201100
Revises: 
Create Date: 2018-05-13 12:48:41.506620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5718ce201100'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tb_apartments',
    sa.Column('tb_apartment_id', sa.Integer(), nullable=False),
    sa.Column('mls_apartment_id', sa.Integer(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('city', sa.String(), nullable=False),
    sa.Column('city_region', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('distance_to_bus', sa.Float(), nullable=True),
    sa.Column('distance_to_school', sa.Float(), nullable=True),
    sa.Column('distance_to_school_bus', sa.Float(), nullable=True),
    sa.Column('distance_to_shopping', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('tb_apartment_id'),
    sa.UniqueConstraint('tb_apartment_id')
    )
    op.create_index(op.f('ix_tb_apartments_mls_apartment_id'), 'tb_apartments', ['mls_apartment_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tb_apartments_mls_apartment_id'), table_name='tb_apartments')
    op.drop_table('tb_apartments')
    # ### end Alembic commands ###