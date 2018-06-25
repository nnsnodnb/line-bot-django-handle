import requests
import socket

BASE_HOST = '127.0.0.1'
PORT = 4040


class Client(object):

    def __init__(self, base_host=BASE_HOST, port=PORT, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.base_host = base_host
        self.port = port
        self._check_launch_ngrok()

    def _check_launch_ngrok(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.base_host, self.port))
        # error handling: socket.error
        s.close()

    def get_public_url(self):
        response = requests.get(f'http://{self.base_host}:{self.port}/api/tunnels').json()
        tunnels = response['tunnels']
        tunnel = tunnels[0]
        public_url = tunnel['public_url']
        return public_url
