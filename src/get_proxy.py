from flask import Blueprint, Response
import requests
from urllib.parse import unquote
from flask_cors import CORS

get_proxy_bp = Blueprint('get_proxy', __name__)
CORS(get_proxy_bp)

@get_proxy_bp.route('/get_proxy/<path:url>', methods=['GET'])
def proxy_request(url):
    try:
        decoded_url = unquote(url)
        
        response = requests.get(decoded_url, stream=True, headers=headers)
        headers = dict(response.headers)
        headers.pop('Content-Encoding', None)
        headers.pop('Transfer-Encoding', None)

        def generate():
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
                yield chunk

        return Response(
            generate(),
            status=response.status_code,
            headers=headers
        )
    
    except Exception as e:
        return {'error': str(e)}, 40
