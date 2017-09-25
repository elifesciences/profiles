from alembic import op
import sqlalchemy as sa

revision = 'b619f44789e4'
down_revision = '14f5651419ad'
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

    profiles = connection.execute(
        profile_helper.select().where(profile_helper.c.preferred_name == ''))

    for profile in profiles:
        connection.execute(
            profile_helper.update().where(
                profile_helper.c.id == profile.id
            ).values(
                index_name='(Unknown)',
                preferred_name='(Unknown)'
            )
        )


def downgrade():
    connection = op.get_bind()

    profiles = connection.execute(
        profile_helper.select().where(profile_helper.c.preferred_name == '(Unknown)'))

    for profile in profiles:
        connection.execute(
            profile_helper.update().where(
                profile_helper.c.id == profile.id
            ).values(
                index_name='',
                preferred_name=''
            )
        )
