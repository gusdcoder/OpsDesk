"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='viewer'),
        sa.Column('mfa_enabled', sa.Boolean(), server_default='false'),
        sa.Column('mfa_secret', sa.String(32), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_users_email', 'email')
    )
    
    # Create hosts table
    op.create_table(
        'hosts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hostname', sa.String(255), nullable=False),
        sa.Column('fqdn', sa.String(255), nullable=True),
        sa.Column('ip', sa.String(45), nullable=False),
        sa.Column('os', sa.String(50), nullable=False),
        sa.Column('environment', sa.String(50), server_default='dev'),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('team', sa.String(255), nullable=True),
        sa.Column('criticality', sa.String(50), server_default='low'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('connection_method', sa.String(50), server_default='direct_ssh'),
        sa.Column('smb_template', sa.Text(), nullable=True),
        sa.Column('ssh_template', sa.Text(), nullable=True),
        sa.Column('bastion_host', sa.String(255), nullable=True),
        sa.Column('bastion_port', sa.Integer(), server_default='22'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_hosts_hostname', 'hostname'),
        sa.Index('idx_hosts_ip', 'ip')
    )
    
    # Create artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by_user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id']),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id']),
        sa.Index('idx_artifacts_host_id', 'host_id')
    )
    
    # Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(50), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(512), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id']),
        sa.Index('idx_audit_events_action', 'action'),
        sa.Index('idx_audit_events_actor_user_id', 'actor_user_id'),
        sa.Index('idx_audit_events_created_at', 'created_at')
    )
    
    # Create metrics_snapshots table
    op.create_table(
        'metrics_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=False),
        sa.Column('collected_by_user_id', sa.Integer(), nullable=False),
        sa.Column('collected_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('source', sa.String(50), server_default='prometheus'),
        sa.Column('ttl_expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id']),
        sa.ForeignKeyConstraint(['collected_by_user_id'], ['users.id']),
        sa.Index('idx_metrics_snapshots_host_id', 'host_id'),
        sa.Index('idx_metrics_snapshots_ttl_expires_at', 'ttl_expires_at')
    )
    
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_settings_key', 'key')
    )

def downgrade() -> None:
    op.drop_table('settings')
    op.drop_table('metrics_snapshots')
    op.drop_table('audit_events')
    op.drop_table('artifacts')
    op.drop_table('hosts')
    op.drop_table('users')
