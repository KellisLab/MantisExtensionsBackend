import mantis_sdk.config as config
import os
from dotenv import load_dotenv

load_dotenv ()
load_dotenv (".env.development", override=True)

config.HOST = os.environ.get ("HOST")
config.DOMAIN = os.environ.get ("DOMAIN")

from mantis_sdk.client import MantisClient, SpacePrivacy, DataType, ReducerModels
from mantis_sdk.space import Space
from mantis_sdk.render_args import RenderArgs

from flask import Flask, request, jsonify
from flask_cors import cross_origin
from urllib.parse import urljoin, urlparse
import pandas as pd
import requests
import uuid
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

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
        
        # Create space with provided parameters
        space_response = mantis.create_space(
            space_name=name + " - " + str(uuid.uuid4()),
            data=df,
            data_types=data.get('data_types', {}),
            reducer=data.get('reducer', ReducerModels.UMAP),
            privacy_level=data.get('privacy_level', SpacePrivacy.PRIVATE)
        )
        
        return jsonify(space_response)
    
    except Exception as e:
        tb = traceback.format_exc()
        
        return jsonify({"error": str(e), "stacktrace": tb}), 400
    
if __name__ == '__main__':
    app.run(port=5111, debug=True)