from alembic import op
import sqlalchemy as sa

revision = '59a7cdca7cb0'
down_revision = '9f896b51fce1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'email_address',
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('restricted', sa.Boolean(), nullable=False),
        sa.Column('profile_id', sa.String(length=8), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], onupdate='CASCADE',
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('email')
    )


def downgrade():
    op.drop_table('email_address')
