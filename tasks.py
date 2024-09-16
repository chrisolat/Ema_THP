
from celery import Celery
from config import Config
from models import db, FileMetadata, JobStatus, AIData
from datetime import datetime
import boto3
import json

celery = Celery('tasks', broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

s3_client = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)

@celery.task
def transform_file(job_id, file_id):
    job_status = JobStatus.query.get(job_id)
    file_metadata = FileMetadata.query.get(file_id)

    try:
        # Update job status
        job_status.status = 'In Progress'
        job_status.progress = 0
        db.session.commit()

        # Simulate downloading the file
        s3_response = s3_client.get_object(Bucket=Config.AWS_S3_BUCKET, Key=file_metadata.location)
        file_content = s3_response['Body'].read()

        # Simulate transformation
        # Here, we'll just count the words as a placeholder
        word_count = len(file_content.decode('utf-8').split())
        ai_data = AIData(
            file_id=file_id,
            transformation_type='WordCount',
            data={'word_count': word_count}
        )
        db.session.add(ai_data)

        # Update job status
        job_status.status = 'Completed'
        job_status.progress = 100
        job_status.completed_at = datetime.utcnow()
        file_metadata.status = 'Ready'
        db.session.commit()
    except Exception as e:
        job_status.status = 'Failed'
        job_status.error_message = str(e)
        file_metadata.status = 'Error'
        db.session.commit()
        raise e
