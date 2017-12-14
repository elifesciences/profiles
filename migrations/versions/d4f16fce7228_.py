from alembic import op
import sqlalchemy as sa

revision = 'd4f16fce7228'
down_revision = '6e06221b94fa'
branch_labels = None
depends_on = None

affiliation_helper = sa.Table(
    'affiliation',
    sa.MetaData(),
    sa.Column('starts_year', sa.Integer()),
)


def upgrade():
    op.alter_column('affiliation', 'starts_year', nullable=True)


def downgrade():
    connection = op.get_bind()

    connection.execute(affiliation_helper.delete().where(affiliation_helper.c.starts_year == None))

    op.alter_column('affiliation', 'starts_year', nullable=False)
