import argparse
from dotenv import load_dotenv
from mantis_sdk.client import MantisClient, SpacePrivacy, ReducerModels
from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
from flask_caching import Cache
import pandas as pd
import traceback
import logging
import uuid
import os

from get_proxy import get_proxy_bp

logging.basicConfig(level=logging.DEBUG)

# Create app with CORS functionality
app = Flask(__name__)
CORS(app)

# Setup simple caching
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

app.register_blueprint(get_proxy_bp)

@app.route('/create-space', methods=['POST'])
@cross_origin()
def create_space():
    try:
        # Extract data from the request
        data = request.json
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
            
            # Update the cache with the job ID -> space_id
            job_space_id_cache = cache.get("job_space_id")

            if job_space_id_cache is None:
                job_space_id_cache = {}

            job_space_id_cache[job_id] = (space_id, layer_id)

            # reset the value
            cache.set("job_space_id", job_space_id_cache)

        # Main SDK call to create space
        space_response = mantis.create_space(
            space_name=name + " - " + str(uuid.uuid4()),
            data=df,
            data_types=data.get('data_types', {}),
            reducer=data.get('reducer', ReducerModels.UMAP),
            privacy_level=data.get('privacy_level', SpacePrivacy.PRIVATE),
            on_recieve_id=on_recieve_id
        )

        return jsonify(space_response)
    
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "stacktrace": tb}), 400

@app.route('/get-space-id/<job>', methods=['GET'])
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    args = parser.parse_args()

    load_dotenv()

    if args.production:
        app.config["ENV"] = "production"
        app.config["DEBUG"] = False
    else:
        load_dotenv (".env.development", override=True)

        app.config["ENV"] = "development"
        app.config["DEBUG"] = True

    app.run(host="0.0.0.0", port=8111, debug=app.config["DEBUG"])
