import mantis_sdk.config as config
from dotenv import load_dotenv
import os

load_dotenv ()
load_dotenv (".env.development", override=True)

config.HOST = os.environ.get ("HOST")
config.DOMAIN = os.environ.get ("DOMAIN")

from mantis_sdk.client import MantisClient, SpacePrivacy, ReducerModels

from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
from flask_caching import Cache
import pandas as pd
import traceback
import logging
import uuid

from get_proxy import get_proxy_bp

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

app.config['CACHE_TYPE'] = 'simple'  # In-memory caching
cache = Cache(app)

app.register_blueprint(get_proxy_bp)

@app.route('/create-space', methods=['POST'])
@cross_origin()
def create_space():
    try:
        data = request.json
        mantis = MantisClient("/api/proxy/", data.get('cookie'))
        
        # Create DataFrame from input data
        df = pd.DataFrame(data.get('data', {}))
        
        name = data.get('name', "Connection")
        if not name:
            name = "Connection"

        # When a space_id is recieved, store it in cache (for future reference)
        def on_recieve_id (space_id):
            job_space_id_cache = cache.get ("job_space_id")
            job_id = data.get ("job")

            if job_id is None:
                return

            if job_space_id_cache is None:
                job_space_id_cache = {}

            job_space_id_cache[job_id] = space_id

            cache.set ("job_space_id", job_space_id_cache)
        
        # Create space with provided parameters
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
            
        space_id = job_space_id_cache[job]
        return jsonify({"space_id": space_id})
        
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"error": str(e), "stacktrace": tb}), 400
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8111, debug=True)
