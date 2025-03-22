import traceback
import uuid
import pandas as pd
from mantis_sdk.client import MantisClient, SpacePrivacy, ReducerModels
from src.extensions import celery
import redis

# Create a redis connection
redis_cache = redis.Redis(host='redis', port=6379, decode_responses=True)

@celery.task
def process_space_creation(data):
    try:
        df = pd.DataFrame(data.get('data', {}))

        # Create mantis client
        mantis = MantisClient("/api/proxy/", data.get('cookie'))

        # Name of connection to create
        name = data.get('name', "Connection") or "Connection"

        def on_recieve_id(space_id, layer_id):
            # Get job ID, exit if not found
            job_id = data.get("job")
            if job_id is None:
                return
            
            # Update the cache with the specific job as a unique dict and store the space_id and layer_id
            redis_cache.hset(f"job_space_id:{job_id}", "space_id", space_id)
            redis_cache.hset(f"job_space_id:{job_id}", "layer_id", layer_id)

        # Main SDK call to create space
        space_response = mantis.create_space(
            space_name=name + " - " + str(uuid.uuid4()),
            data=df,
            data_types=data.get('data_types', {}),
            reducer=data.get('reducer', ReducerModels.UMAP),
            privacy_level=data.get('privacy_level', SpacePrivacy.PRIVATE),
            on_recieve_id=on_recieve_id
        )
            
        return space_response
    except Exception as e:
        return {"error": str(e), "stacktrace": traceback.format_exc()}