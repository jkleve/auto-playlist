import os
import re
import requests
from collections import namedtuple
from urllib.parse import ParseResult
from util.log import log_info, log_error

Url = namedtuple('Url', 'host path')


def convert(url: ParseResult) -> Url:
    return Url(url.netloc, url.path)


def get_track_id(url):
    """Get base-62 encoded track ID"""
    m = re.search('/track/(?P<track_id>[a-zA-Z0-9]+)$', url.path)
    try:
        return m.group('track_id')
    except (AttributeError, IndexError):
        log_info(f'{url.path} does not appear to be a spotify track')


def get_playlist_id():
    """Get from enviornment for now"""
    return os.getenv('SPOTIFY_PLAYLIST_ID')


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
            if track_id := self.get_track_id(url):
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
