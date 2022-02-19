import redis
from flask import current_app, g


def init_db():
    pass


def get_db():
    if 'db' not in g:
        g.db = redis.Redis(
            # host=current_app.config['DATABASE'], # @todo get or default host and port
            host='redis',
            port=6379,
        ),
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()