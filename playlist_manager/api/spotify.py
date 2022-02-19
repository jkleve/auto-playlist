import json
import os
import re
import redis
import requests
from base64 import b64encode
from collections import namedtuple
from datetime import datetime, timedelta
from flask import Flask, redirect, request, make_response, Response
from urllib.parse import urlencode, urlparse
from urllib.parse import ParseResult
from util.log import log_debug, log_info, log_error

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

Url = namedtuple('Url', 'host path')


def convert(url: ParseResult) -> Url:
    return Url(url.netloc, url.path)


def get_track_id(path):
    """Get base-62 encoded track ID"""
    m = re.search('/track/(?P<track_id>[a-zA-Z0-9]+)$', path)
    try:
        return m.group('track_id')
    except (AttributeError, IndexError):
        log_info(f'{path} does not appear to be a spotify track')


def get_playlist_id():
    """Get from enviornment for now"""
    return os.getenv('SPOTIFY_PLAYLIST_ID')


def login(ctx, request):
    query_params = {
        'response_type': 'code',
        'client_id': ctx['spotify']['client_id'],
        'redirect_uri': f'{request.host_url}callback/',
        'scope': 'playlist-modify-public',
    }
    return redirect(f"https://accounts.spotify.com/authorize?{urlencode(query_params)}")


def encode_secrets(client_id, client_secret):
    return b64encode(f'{client_id}:{client_secret}'.encode('utf8')).decode('utf8')


def callback(ctx):
    # @todo how slow is it to have this method hang while it sends request to spotify.com?
    log_info(f'trying code: {request.args.get("code")}')

    response = requests.post('https://accounts.spotify.com/api/token',
        headers={'Authorization': f'Basic {encode_secrets(ctx["client_id"], ctx["client_secret"])}'},
        data={
            'grant_type': 'authorization_code',
            'redirect_uri': f'{request.host_url}callback/',
            'code': request.args.get('code'),
        })

    if response.ok:
        token = response.json()['access_token']
        ctx['db'].set('access_token', token)
        ctx['db'].set('refresh_token', response.json()['refresh_token'])
        log_debug(f'access_token: {token}')
        log_debug(f'access_token: {token}')
    else:
        log_error(f'{response.status_code}: {response.text}')

    return ''


class OAuthMgr(object):
    """Manages the OAuth for Spotify"""
    def __init__(self, ctx):
        self.ctx = ctx

        self.access = self._load_access()
        self.refreshed_at = None

        self.refresh_session()

    @property
    def access_token(self):
        return self.access["access_token"]

    def is_expired(self):
        """Checks if the time now is greater than the token's expiration time plus 60 seconds of buffer"""
        return datetime.utcnow() > self.refreshed_at + timedelta(seconds=self.access["expires_in"] + 60)

    def _load_access(self):
        return dict(
            access_token=self.db.get('access_token'),
            refresh_token=self.db.get('refresh_token'),
        )

    def _save_access(self):
        self.db.set('access_token', self.access['access_token'])
        self.db.set('refresh_token', self.access['refresh_token'])

    def refresh_session(self):
        log_debug('refreshing access token')

        response = requests.post('https://accounts.spotify.com/api/token',
            headers={'Authorization': f'Basic {encode_secrets(self.ctx["client_id"], self.ctx["client_secret"])}'},
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.access['refresh_token'],
            })

        if response.status_code == requests.codes.ok:
            log_debug('got new access token')
            self.access.update(json.loads(response.text))
            self.refreshed_at = datetime.utcnow()
            self._save_access()
        else:
            log_error(f'failed to refresh access token: {response.text}')


class SpotifyHandler(object):
    def __init__(self):
        # self.oauth = self.OAuthMgr()
        pass

    def handle(self, urllib_url: ParseResult):
        self.handle_url(convert(urllib_url))

    def handle_url(self, url: Url):
        if 'spotify' in url.host:
            # @todo need oauth access token
            # - how do we update it every 3600 seconds?
            # - how do we initialize it to something?
            # - how do we fix it if it breaks?
            #
            # - get it from a redis instance
            #   - we'd need to initialize it with a bot or UI
            #   - 
            #
            # if self.oauth.is_expired():
            #     self.oauth.refresh_session()
            if track_id := self.get_track_id(url.path):
                self.add(get_playlist_id(), f'spotify:track:{track_id}')


    def add(self, playlist_id, track_uri):
        log_info(f'add {track_uri} to spotify:playlist:{playlist_id}')

        response = requests.post(
            f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
            headers={'Authorization': f'Bearer {self.oauth.access_token}'},
            params={'uris': track_uri},
        )

        if response.ok:
            log_info(f'added {track_uri} to {playlist_id}')
        else:
            log_error(f'failed to add tracks {track_uri}: {response.text}')
