"""Added product_price column to the order_product table.

Revision ID: 57f3ea2d076b
Revises: fd4b0be3144f
Create Date: 2022-09-02 03:54:57.594151

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57f3ea2d076b'
down_revision = 'fd4b0be3144f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_product', sa.Column('product_price', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_product', 'product_price')
    # ### end Alembic commands ###
