"""
Module to perform file transformations/ other file processing.
"""

from tasks import transform_file
from permissions import check_permission
from decorators import permission_required
from models import db, FileMetadata, JobStatus
from flask_login import login_required, current_user

@files_bp.route('/<file_id>/transform', methods=['POST'])
@login_required
@permission_required('can_write')
def initiate_transformation(file_id):
    file_metadata = FileMetadata.query.get(file_id)
    if not file_metadata:
        return jsonify({'error': 'File not found'}), 404

    # Check permissions
    if not check_permission(current_user.user_id, file_id, 'can_write'):
        return jsonify({'error': 'Access denied'}), 403

    job_id = str(uuid.uuid4())
    job_status = JobStatus(
        job_id=job_id,
        file_id=file_id,
        status='Pending',
        progress=0,
        started_at=datetime.utcnow()
    )
    db.session.add(job_status)
    file_metadata.status = 'Transforming'
    db.session.commit()

    # Start transformation task
    transform_file.delay(job_id, file_id)

    return jsonify({'message': 'Transformation initiated', 'job_id': job_id}), 202
