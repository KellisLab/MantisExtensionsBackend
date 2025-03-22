import traceback
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.tasks.space_tasks import process_space_creation
import redis

space = Blueprint('space', __name__)
redis_cache = redis.Redis(host='redis', port=6379, decode_responses=True)

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

@space.route('/space-task-status/<task_id>', methods=['GET'])
@cross_origin()
def task_status(task_id):
    task = process_space_creation.AsyncResult(task_id)
    response = {"state": task.state}

    if task.state != 'FAILURE':
        if task.info and 'error' in task.info:
            response["stacktrace"] = task.info.get('stacktrace', '')
        else:
            response["result"] = task.info
    else:
        response["error"] = str(task.info)

    return jsonify(response)

@space.route('/get-space-id/<job>', methods=['GET'])
@cross_origin()
def get_space_id(job):
    try:
        space_id = redis_cache.hget(f"job_space_id:{job}", "space_id")
        layer_id = redis_cache.hget(f"job_space_id:{job}", "layer_id")

        if space_id is None or layer_id is None:
            return jsonify({"error": "No space found for this job"}), 404
        
        return jsonify({"space_id": space_id, "layer_id": layer_id})
    
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "stacktrace": tb}), 400