from alembic import op
import sqlalchemy as sa

revision = 'b35b975485ce'
down_revision = 'f17777978680'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'affiliation',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('department', sa.Text(), nullable=True),
        sa.Column('organisation', sa.Text(), nullable=False),
        sa.Column('city', sa.Text(), nullable=False),
        sa.Column('region', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('restricted', sa.Boolean(), nullable=False),
        sa.Column('profile_id', sa.String(length=8), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], onupdate='CASCADE',
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('affiliation')
