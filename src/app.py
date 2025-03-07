import mantis_sdk.config as config
import os
import json
from dotenv import load_dotenv

load_dotenv ()
load_dotenv (".env.development", override=True)

config.HOST = os.environ.get ("HOST")
config.DOMAIN = os.environ.get ("DOMAIN")

from mantis_sdk.client import MantisClient, SpacePrivacy, DataType, ReducerModels
from mantis_sdk.space import Space
from mantis_sdk.render_args import RenderArgs

from flask import Flask, request, jsonify, Response
from flask_cors import cross_origin
from urllib.parse import urljoin, urlparse
import pandas as pd
import requests
import uuid
import traceback
import logging

from get_proxy import get_proxy_bp

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.register_blueprint(get_proxy_bp)

@app.route('/create-space-sse', methods=['GET'])
@cross_origin()
def create_space_sse():
    def format_yield (data):
        return f"data: {json.dumps(data)}\n\n"
        
    def event_stream():
        try:
            name = request.args.get('name', "Connection")
            cookie = request.args.get('cookie', "")
            data_types = json.loads(request.args.get('data_types', '{}'))
            data_param = request.args.get('data', '{}')
            data_json = json.loads(data_param)
            reducer = request.args.get('reducer', None)
            privacy_level = request.args.get('privacy_level', None)
            
            mantis = MantisClient("/api/proxy/", cookie)
            
            # Convert input data into a DataFrame
            df = pd.DataFrame(data_json)
            
            def on_recieve_id (space_id):
                yield format_yield({"type": "space_id", "value": space_id})
            
            # Create the space
            space_response = mantis.create_space(
                space_name=name + " - " + str(uuid.uuid4()),
                data=df,
                data_types=data_types,
                reducer=reducer if reducer else ReducerModels.UMAP,
                privacy_level=privacy_level if privacy_level else SpacePrivacy.PRIVATE,
                on_recieve_id=on_recieve_id
            )
            
            yield format_yield({"type": "completed", "value": space_response})

        except Exception as e:
            tb = traceback.format_exc()

            yield format_yield({"type": "error", "value": {"error": str(e), "stacktrace": tb}})

    return Response(event_stream(), mimetype="text/event-stream")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8111, debug=True)
