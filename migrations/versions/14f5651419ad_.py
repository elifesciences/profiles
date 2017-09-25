from alembic import op
import sqlalchemy as sa

from profiles.utilities import string_to_name

revision = '14f5651419ad'
down_revision = '9f896b51fce1'
branch_labels = None
depends_on = None

profile_helper = sa.Table(
    'profile',
    sa.MetaData(),
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('given_names', sa.Text(), nullable=False),
    sa.Column('family_name', sa.Text(), nullable=True),
)


def upgrade():
    connection = op.get_bind()

    op.add_column('profile', sa.Column('family_name', sa.Text()))
    op.add_column('profile', sa.Column('given_names', sa.Text()))

    for profile in connection.execute(profile_helper.select()):
        name = string_to_name(profile.name)
        connection.execute(
            profile_helper.update().where(
                profile_helper.c.id == profile.id
            ).values(
                given_names=name.given_names,
                family_name=name.family_name
            )
        )

    op.drop_column('profile', 'name')
    op.alter_column('profile', 'given_names', nullable=False)


def downgrade():
    connection = op.get_bind()

    op.add_column('profile', sa.Column('name', sa.Text()))

    for profile in connection.execute(profile_helper.select()):
        connection.execute(
            profile_helper.update().where(
                profile_helper.c.id == profile.id
            ).values(
                name="{} {}".format(profile.given_names, profile.family_name)
            )
        )

    op.drop_column('profile', 'given_names')
    op.drop_column('profile', 'family_name')
    op.alter_column('profile', 'name', nullable=False)
