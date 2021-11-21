from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading

from .record import start_tracing
from .record import stop_tracing
from .record import get_output

PORT_NUMBER = 9135
web_server = None


class RemoteServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/pynsights')
        self.end_headers()
        if self.path == "/trace":
            self.send_trace()
        elif self.path == "/start":
            start_tracing()
        elif self.path == "/stop":
            stop_tracing()
        elif self.path == "/exit":
            os._exit(4)

    def send_trace(self):
        path = get_output()
        print("Pynsights: Remote control opening", path)
        if os.path.exists(path):
            with open(path) as fp:
                lines = fp.readlines()
                for line in lines:
                    self.wfile.write(bytes(line, 'utf8'))


def listen(portNumber = PORT_NUMBER):
    global web_server
    web_server = HTTPServer(("localhost", portNumber), RemoteServer)
    print("Pynsights: remote access server started http://localhost:%s/trace" % (portNumber))
    threading.Thread(target=run).start()


def run():
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass
    web_server.server_close()
    print("Pynsights remote access server stopped.")