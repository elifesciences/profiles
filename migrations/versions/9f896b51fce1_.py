from alembic import op
import sqlalchemy as sa

revision = '9f896b51fce1'
down_revision = 'e1b6d52fd6ea'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'orcid_token',
        sa.Column('orcid', sa.String(length=19), nullable=False),
        sa.Column('access_token', sa.String(length=255), nullable=True),
        sa.Column('expires', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('orcid'),
        sa.UniqueConstraint('access_token')
    )


def downgrade():
    op.drop_table('orcid_token')
