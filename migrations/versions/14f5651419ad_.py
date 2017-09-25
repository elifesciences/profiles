from alembic import op
import sqlalchemy as sa

from profiles.utilities import guess_index_name

revision = '14f5651419ad'
down_revision = '9f896b51fce1'
branch_labels = None
depends_on = None

profile_helper = sa.Table(
    'profile',
    sa.MetaData(),
    sa.Column('id', sa.String(length=8), nullable=False),
    sa.Column('preferred_name', sa.Text(), nullable=False),
    sa.Column('index_name', sa.Text(), nullable=True),
)


def upgrade():
    connection = op.get_bind()

    op.alter_column('profile', 'name', new_column_name='preferred_name')
    op.add_column('profile', sa.Column('index_name', sa.Text()))

    for profile in connection.execute(profile_helper.select()):
        connection.execute(
            profile_helper.update().where(
                profile_helper.c.id == profile.id
            ).values(
                index_name=guess_index_name(profile.preferred_name)
            )
        )

    op.alter_column('profile', 'index_name', nullable=False)


def downgrade():
    op.alter_column('profile', 'preferred_name', new_column_name='name')
    op.drop_column('profile', 'index_name')
