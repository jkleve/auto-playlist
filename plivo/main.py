from flask import Flask, request, make_response, Response
from plivo import plivoxml
import requests
import sys

__author__ = 'Jesse Kleve'
__version__ = '0.1.0'

app = Flask(__name__)


def log_info(msg):
    print(msg)


def log_error(msg):
    print(msg)


def forward_msg(msg):
    # @todo asyncio
    host = 'http://api:5001'
    try:
        response = requests.post(f'{host}/messages/', data={'msg': msg})
    except requests.exceptions.ConnectionError:
        log_error(f"can't connect to {host}")
    else:
        if not response.ok:
            log_error(f'{response.status_code}:{response.text}')


@app.route('/sms/', methods=['POST'])
def sms():
    # @todo check if request.host_url is from plivo.com. if not, log 'blocking bitch bot' and return
    # or the host needs to be in the 'accept list'. so i can debug from my laptop. but then i'd need a static ip...
    try:
        msg = request.json.get('msg')
        log_info(f'sms: {msg}')
    except AttributeError:
        error = f'missing "msg" on sms post request'
        log_error(error)
        return error, requests.codes.bad_request
    else:
        forward_msg(msg)
    return 'ok'


@app.route('/health/', methods=['GET'])
def health():
    response = plivoxml.ResponseElement()
    response.add(plivoxml.MessageElement("ok"))
    return Response(response.to_string(), mimetype='application/xml')


if __name__ == '__main__':
    if app.debug:
        app.run(host='localhost', port=8080)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8080)
