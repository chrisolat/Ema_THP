"""
File service api to handle file uploads, downloads, etc..
"""
from flask import Blueprint, request, jsonify, send_file
from models import db, FileMetadata, JobStatus
from flask_login import login_required, current_user
import uuid
import boto3
from config import Config
from permissions import check_permission
from datetime import datetime
from decorators import permission_required

from confluent_kafka import Producer
import socket

conf = {'bootstrap.servers': 'pkc-abcd85.us-west-2.aws.confluent.cloud:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': '<CLUSTER_API_KEY>',
        'sasl.password': '<CLUSTER_API_SECRET>',
        'client.id': socket.gethostname()}


files_bp = Blueprint('files', __name__)

s3_client = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)

# notify file worker service when file upload happens
def produce_confluent_message(topic,key,value):
    producer = Producer(conf)
    producer.produce(topic, key, value)

@files_bp.route('/', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    file_id = str(uuid.uuid4())
    s3_key = f"{current_user.user_id}/{file_id}/{file.filename}"
    s3_client.upload_fileobj(file, Config.AWS_S3_BUCKET, s3_key)
    # need code to show upload status updates
    file_metadata = FileMetadata(
        file_id=file_id,
        name=file.filename,
        owner_id=current_user.user_id,
        size=request.content_length,
        type=file.content_type,
        status='Uploaded',
        location=s3_key
    )
    db.session.add(file_metadata)
    db.session.commit()
    # add to file processing worker queue
    produce_confluent_message("File_Processing", "file_id", file_id)
    #-----------------------
    return jsonify({'message': 'File uploaded', 'file_id': file_id}), 201

@files_bp.route('/<file_id>', methods=['GET'])
@login_required
@permission_required('can_read')
def download_file(file_id):
    file_metadata = FileMetadata.query.get(file_id)
    if not file_metadata:
        return jsonify({'error': 'File not found'}), 404

    # Check permissions
    if not check_permission(current_user.user_id, file_id, 'can_read'):
        return jsonify({'error': 'Access denied'}), 403

    # Generate a presigned URL for download
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': Config.AWS_S3_BUCKET, 'Key': file_metadata.location},
        ExpiresIn=3600  # URL expires in 1 hour
    )
    return jsonify({'download_url': url}), 200


@files_bp.route('/<file_id>/status', methods=['GET'])
@login_required
def get_file_status(file_id):
    file_metadata = FileMetadata.query.get(file_id)
    if not file_metadata:
        return jsonify({'error': 'File not found'}), 404

    # Check permissions
    if not check_permission(current_user.user_id, file_id, 'can_read'):
        return jsonify({'error': 'Access denied'}), 403

    job_status = JobStatus.query.filter_by(file_id=file_id).order_by(JobStatus.started_at.desc()).first()
    if not job_status:
        status = file_metadata.status
        progress = 100 if status == 'Ready' else 0
    else:
        status = job_status.status
        progress = job_status.progress

    return jsonify({
        'file_id': file_id,
        'status': status,
        'progress': progress
    }), 200
