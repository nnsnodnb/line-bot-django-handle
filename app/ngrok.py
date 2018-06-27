from django.conf import settings

import requests
import socket

BASE_HOST = '127.0.0.1'
PORT = 4040


class Ngrok(object):

    def __init__(self, port=PORT, *args, **kwargs):
        super(Ngrok, self).__init__(*args, **kwargs)
        self.port = port
        self._check_launch_ngrok()

    def _check_launch_ngrok(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((BASE_HOST, self.port))
        # error handling: socket.error
        s.close()

    def get_public_url(self):
        if not settings.USE_NGROK:
            return None
        response = requests.get(f'http://{BASE_HOST}:{self.port}/api/tunnels').json()
        tunnels = response['tunnels']
        tunnel = tunnels[1]
        public_url = tunnel['public_url']
        return public_url
