"""
DB models.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FileMetadata(db.Model):
    __tablename__ = 'file_metadata'
    file_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    size = db.Column(db.BigInteger)
    type = db.Column(db.String(50))
    status = db.Column(db.String(20))
    location = db.Column(db.String(255))  # S3 Key
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Permission(db.Model):
    __tablename__ = 'permissions'
    permission_id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(36), db.ForeignKey('file_metadata.file_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    can_read = db.Column(db.Boolean, default=True)
    can_write = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)
    can_share = db.Column(db.Boolean, default=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIData(db.Model):
    __tablename__ = 'ai_data'
    data_id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(36), db.ForeignKey('file_metadata.file_id'), nullable=False)
    transformation_type = db.Column(db.String(50))
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobStatus(db.Model):
    __tablename__ = 'job_status'
    job_id = db.Column(db.String(36), primary_key=True)
    file_id = db.Column(db.String(36), db.ForeignKey('file_metadata.file_id'), nullable=False)
    status = db.Column(db.String(20))
    progress = db.Column(db.Integer)  # Percentage
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
