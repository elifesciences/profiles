from alembic import op
import sqlalchemy as sa

revision = 'e1b6d52fd6ea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profile',
        sa.Column('id', sa.String(length=8), nullable=False),
        sa.Column('orcid', sa.String(length=19), nullable=True),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('orcid')
    )


def downgrade():
    op.drop_table('profile')
