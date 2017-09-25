from alembic import op
import sqlalchemy as sa

revision = 'b619f44789e4'
down_revision = '14f5651419ad'
branch_labels = None
depends_on = None

profile_helper = sa.Table(
    'profile',
    sa.MetaData(),
    sa.Column('preferred_name', sa.Text(), nullable=False),
)


def upgrade():
    connection = op.get_bind()

    connection.execute(profile_helper.delete().where(profile_helper.c.preferred_name == ''))


def downgrade():
    pass
