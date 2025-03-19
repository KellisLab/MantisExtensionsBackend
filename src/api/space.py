import traceback
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.extensions import cache
from src.tasks.space_tasks import process_space_creation

space = Blueprint('space', __name__)

@space.route('/create-space', methods=['POST'])
@cross_origin()
def create_space():
    try:
        # Extract data from the request
        data = request.json
        
        task = process_space_creation.delay(data)
        
        return jsonify({"task_id": task.id, "status": "processing"})
    
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "stacktrace": tb}), 400

@space.route('/task-status/<task_id>', methods=['GET'])
@cross_origin()
def task_status(task_id):
    task = process_space_creation.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        if task.info and 'error' in task.info:
            response = {
                'state': task.state,
                'status': task.info.get('error', ''),
                'stacktrace': task.info.get('stacktrace', '')
            }
        else:
            response = {
                'state': task.state,
                'result': task.info
            }
    else:
        response = {
            'state': task.state,
            'status': 'Task failed',
            'error': str(task.info)
        }
    return jsonify(response)

@space.route('/get-space-id/<job>', methods=['GET'])
@cross_origin()
def get_space_id(job):
    try:
        job_space_id_cache = cache.get("job_space_id")

        if job_space_id_cache is None or job not in job_space_id_cache:
            return jsonify({"error": "No space found for this job"}), 404
        
        space_id, layer_id = job_space_id_cache[job]

        return jsonify({"space_id": space_id, "layer_id": layer_id})
    
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "stacktrace": tb}), 400