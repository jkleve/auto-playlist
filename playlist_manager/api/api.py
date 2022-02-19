import re
import redis

from flask import Flask, request
from urllib.parse import urlparse
from util.log import log_debug

# @todo create spotify_init method that hides the callback and login functions
# @todo register handler?
from .spotify import SpotifyHandler
from .spotify import callback as spotify_callback
from .spotify import login as spotify_login


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


def create_app(test_config=None):
    """Create the flask app"""

    app = Flask(__name__, instance_relative_config=True)

    handlers = [
        SpotifyHandler(),
    ]

    ctx = {
        'db': redis.Redis(host='redis', port=6379),
        'spotify': {
            'client_id': 'e92e740411d44d3786c109d845d7d480',
            'client_secret': '7adcb3867bbb4b60b2ea848b5d88aac2',
        },
    }

    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    @app.route('/login/', methods=['GET'])
    def login():
        return spotify_login(ctx, request)

    @app.route('/callback/', methods=['GET'])
    def callback():
        return spotify_callback(ctx, request)

    @app.route('/messages/', methods=['POST'])
    def messages():
        log_debug(f"received {request.values.get('msg')}")
        handle_message(request.values.get('msg'), handlers)
        return 'ok'

    @app.route('/health/', methods=['GET'])
    def health():
        return 'ok'

    return app


def run_app(app):
    # @todo port = os.getenv('pl_port')
    if app.debug:
        print('debug')
        app.run(host='localhost', port=8081)
        print('here')
    else:
        print('production')
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
