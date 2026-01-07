"""rename mail_password_hash to encrypted

Revision ID: a1b2c3d4e5f6
Revises: bdb5548afc4c
Create Date: 2026-01-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'bdb5548afc4c'
branch_labels = None
depends_on = None


def upgrade():
    """Rename mail_password_hash to mail_password_encrypted.
    
    Note: Any existing hashed passwords will need to be re-entered by users
    since we cannot convert bcrypt hashes to encrypted passwords.
    """
    # Rename the column
    with op.batch_alter_table('app_settings', schema=None) as batch_op:
        batch_op.alter_column('mail_password_hash',
                            new_column_name='mail_password_encrypted',
                            existing_type=sa.String(255),
                            type_=sa.Text(),
                            nullable=True)


def downgrade():
    """Revert the column name back to mail_password_hash."""
    with op.batch_alter_table('app_settings', schema=None) as batch_op:
        batch_op.alter_column('mail_password_encrypted',
                            new_column_name='mail_password_hash',
                            existing_type=sa.Text(),
                            type_=sa.String(255),
                            nullable=True)
