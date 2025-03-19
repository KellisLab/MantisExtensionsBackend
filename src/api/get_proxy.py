from flask import Blueprint, Response
from flask_cors import cross_origin
from urllib.parse import unquote
import requests

get_proxy = Blueprint('get_proxy', __name__)

@get_proxy.route('/get_proxy/<path:url>', methods=['GET'])
@cross_origin()
def proxy_request(url):
    try:
        decoded_url = unquote(url)
        
        response = requests.get(decoded_url, stream=True)
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