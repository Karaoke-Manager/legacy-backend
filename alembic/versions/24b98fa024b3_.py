"""empty message

Revision ID: 24b98fa024b3
Revises: 
Create Date: 2020-03-25 16:51:16.821242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24b98fa024b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permission',
    sa.Column('name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('name'),
    sa.UniqueConstraint('name')
    )
    op.create_table('role',
    sa.Column('name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.Text(), nullable=False),
    sa.Column('password_hash', sa.String(length=94), nullable=True),
    sa.Column('is_admin', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('role_permissions',
    sa.Column('role_name', sa.Integer(), nullable=False),
    sa.Column('permission_name', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_name'], ['permission.name'], ),
    sa.ForeignKeyConstraint(['role_name'], ['role.name'], ),
    sa.PrimaryKeyConstraint('role_name', 'permission_name')
    )
    op.create_table('user_permissions',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('permission_name', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_name'], ['permission.name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'permission_name')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_name'], ['role.name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_roles')
    op.drop_table('user_permissions')
    op.drop_table('role_permissions')
    op.drop_table('user')
    op.drop_table('role')
    op.drop_table('permission')
    # ### end Alembic commands ###
