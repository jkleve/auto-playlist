from base64 import b64encode
from flask import Flask, redirect, request, make_response, Response
from spotify import SpotifyHandler
from spotify import callback as spotify_callback
from spotify import login as spotify_login
from urllib.parse import urlencode, urlparse
from util.log import log_debug, log_info, log_error

import re
import redis
import requests

__author__ = 'Jesse Kleve'
__version__ = '0.8.0'

"""
Spotify authorization code flow

 1. need to redirect the user to 
   GET https://accounts.spotify.com/api/authorize
     query parameters:
       response_type=code
       client_id=<client id>
       redirect_uri=http://<this host>/callback/
       scope='playlist-modify-public'

 2. need to capture the 'code' paramter on /callback/ route

 3. with the code, make the next request
   POST https://accounts.spotify.com/api/token
     data:
       grant_type=authorization_code
       redirect_uri=http://<this host>:5000
       code=<code>

 4. response has access_token and refresh_token
"""

app = Flask(__name__)
ctx = {
    'db': redis.Redis(host='redis', port=6379),
    'spotify': {
        'client_id': 'e92e740411d44d3786c109d845d7d480',
        'client_secret': '7adcb3867bbb4b60b2ea848b5d88aac2',
    },
}
handlers = [
    SpotifyHandler(),
]


def get_urls(string):
    """Get all url matching strings from string"""
    regex = re.compile(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|
                       (\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))""",
                       re.VERBOSE)
    try:
        url = regex.findall(string)
        return [u[0] for u in url]
    except TypeError:
        return list()


def handle_message(message, handlers):
    """For each url in message, call all handlers"""
    def handle(url):
        u = urlparse(url)
        for handler in handlers:
            handler.handle(u)

    map(handle, get_urls(message))


@app.route('/login/', methods=['GET'])
def login():
    return spotify_login(ctx, request)


@app.route('/callback/', methods=['GET'])
def callback():
    return spotify_callback(ctx, request)


@app.route('/messages/', methods=['POST'])
def messages():
    print(f"received {request.values.get('msg')}")  # @todo create utils and import log_info
    handle_message(request.values.get('msg'), handlers)
    return 'ok'


@app.route('/health/', methods=['GET'])
def health():
    return 'ok'


def main():
    # @todo port = os.getenv('pl_port')
    if app.debug:
        app.run(host='localhost', port=8080)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
