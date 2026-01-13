"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-13 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create incidents table
    op.create_table(
        'incidents',
        sa.Column('incident_id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('type', sa.Enum('crash', 'police', 'road_rage', 'hazard', 'other', name='incidenttype'), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('heading', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('video_path', sa.String(500), nullable=False),
        sa.Column('video_size', sa.BigInteger(), nullable=False),
        sa.Column('processing_status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_incidents_incident_id', 'incidents', ['incident_id'])
    
    # Create detected_vehicles table
    op.create_table(
        'detected_vehicles',
        sa.Column('detection_id', sa.String(36), primary_key=True),
        sa.Column('incident_id', sa.String(36), sa.ForeignKey('incidents.incident_id'), nullable=False),
        sa.Column('vehicle_type', sa.String(50), nullable=False),
        sa.Column('make', sa.String(50), nullable=True),
        sa.Column('model', sa.String(50), nullable=True),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('bounding_box', sa.JSON(), nullable=False),
        sa.Column('frame_timestamp', sa.Float(), nullable=False),
    )
    op.create_index('ix_detected_vehicles_detection_id', 'detected_vehicles', ['detection_id'])
    
    # Create license_plates table
    op.create_table(
        'license_plates',
        sa.Column('plate_id', sa.String(36), primary_key=True),
        sa.Column('incident_id', sa.String(36), sa.ForeignKey('incidents.incident_id'), nullable=False),
        sa.Column('detection_id', sa.String(36), sa.ForeignKey('detected_vehicles.detection_id'), nullable=True),
        sa.Column('plate_number', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('state_region', sa.String(50), nullable=True),
        sa.Column('country', sa.String(50), nullable=True),
        sa.Column('frame_timestamp', sa.Float(), nullable=False),
        sa.Column('bounding_box', sa.JSON(), nullable=False),
    )
    op.create_index('ix_license_plates_plate_id', 'license_plates', ['plate_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_license_plates_plate_id', 'license_plates')
    op.drop_table('license_plates')
    
    op.drop_index('ix_detected_vehicles_detection_id', 'detected_vehicles')
    op.drop_table('detected_vehicles')
    
    op.drop_index('ix_incidents_incident_id', 'incidents')
    op.drop_table('incidents')
    
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
