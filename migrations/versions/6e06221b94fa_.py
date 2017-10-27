from calendar import monthrange
from datetime import datetime

from alembic import op
import sqlalchemy as sa

revision = '6e06221b94fa'
down_revision = 'b35b975485ce'
branch_labels = None
depends_on = None

affiliation_helper = sa.Table(
    'affiliation',
    sa.MetaData(),
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('starts', sa.DateTime(), nullable=True),
    sa.Column('ends', sa.DateTime(), nullable=True),
    sa.Column('starts_year', sa.Integer(), nullable=True),
    sa.Column('starts_month', sa.Integer(), nullable=True),
    sa.Column('starts_day', sa.Integer(), nullable=True),
    sa.Column('ends_year', sa.Integer(), nullable=True),
    sa.Column('ends_month', sa.Integer(), nullable=True),
    sa.Column('ends_day', sa.Integer(), nullable=True),
)


def upgrade():
    connection = op.get_bind()

    op.add_column('affiliation', sa.Column('starts_year', sa.Integer(), nullable=True))
    op.add_column('affiliation', sa.Column('starts_month', sa.Integer(), nullable=True))
    op.add_column('affiliation', sa.Column('starts_day', sa.Integer(), nullable=True))
    op.add_column('affiliation', sa.Column('ends_year', sa.Integer(), nullable=True))
    op.add_column('affiliation', sa.Column('ends_month', sa.Integer(), nullable=True))
    op.add_column('affiliation', sa.Column('ends_day', sa.Integer(), nullable=True))

    for affiliation in connection.execute(affiliation_helper.select()):
        values = {
            'starts_year': affiliation.starts.year,
            'starts_month': affiliation.starts.month,
            'starts_day': affiliation.starts.day,
        }

        if affiliation.ends:
            values['ends_year'] = affiliation.ends.year
            values['ends_month'] = affiliation.ends.month
            values['ends_day'] = affiliation.ends.day

        connection.execute(
            affiliation_helper.update().where(
                affiliation_helper.c.id == affiliation.id
            ).values(**values)
        )

    op.alter_column('affiliation', 'starts_year', nullable=False)

    op.drop_column('affiliation', 'starts')
    op.drop_column('affiliation', 'ends')


def downgrade():
    connection = op.get_bind()

    op.add_column('affiliation', sa.Column('starts', sa.DateTime(), nullable=True))
    op.add_column('affiliation', sa.Column('ends', sa.DateTime(), nullable=True))

    for affiliation in connection.execute(affiliation_helper.select()):
        starts = datetime(affiliation.starts_year, affiliation.starts_month or 1,
                          affiliation.starts_day or 1),

        if affiliation.ends_year:
            ends = datetime(affiliation.ends_year, affiliation.ends_month or 12,
                            affiliation.ends_day or
                            monthrange(affiliation.ends_year, affiliation.ends_month or 12)[1])
        else:
            ends = None

        connection.execute(
            affiliation_helper.update().where(
                affiliation_helper.c.id == affiliation.id
            ).values(starts=starts, ends=ends)
        )

    op.alter_column('affiliation', 'starts', nullable=False)

    op.drop_column('affiliation', 'starts_year')
    op.drop_column('affiliation', 'starts_month')
    op.drop_column('affiliation', 'starts_day')
    op.drop_column('affiliation', 'ends_year')
    op.drop_column('affiliation', 'ends_month')
    op.drop_column('affiliation', 'ends_day')
