"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import inspect
import threading
import time
import collections
import json
import os
import sys
import webbrowser
import http.server

MY_NAME = "pynsights"
PORT = 8974
TRACER_MODULE_NAME = "tracer"
CALL_BUFFER_TIME = 0.3

codes = collections.defaultdict(dict)
frames = []
alive = False
modules = {}


class CallsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.main()
        else:
            self.send_calls()
    
    def main(self):
        self.send_response(200)
        self.send_header('Content-type', "text/html; charset=UTF-8")
        self.end_headers()
        path = os.path.join(os.path.dirname(__file__), "pynsights.html")
        with open(path) as fp:
            self.wfile.write(bytes(fp.read(), 'utf8'))

    def send_calls(self):
        global alive, frames
        alive = True
        snapshot, frames = frames, []
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        data = json.dumps([convert_frame(frame) for frame in snapshot])
        self.wfile.write(bytes(data, 'utf8'))

    def log_message(self, format, *args):
        return


class ServerThread(threading.Thread):
    def run(self):
        server = http.server.HTTPServer(("localhost", PORT), CallsHandler)
        server.serve_forever()


def safe_repr(obj):
    try:
        return repr(obj)
    except:
        return f"[{type(obj)}]"


def get_module(frame):
    key = frame.f_code.co_filename
    if key in modules:
        return modules[key]
    module = inspect.getmodule(frame).__name__
    modules[key] = module
    return module
    

def extract_details(frame):
    return {
        "codename": frame.f_code.co_name,
        "filename": frame.f_code.co_filename,
        "lineno": frame.f_code.co_firstlineno,
        "module": get_module(frame),
    }


def convert_frame(frame):
    try:
        call_to = extract_details(frame)
        call_from = extract_details(frame.f_back)
        if call_to["module"] == call_from["module"]:
            return None
        call = codes[f"""{call_to["module"]}>{call_from["module"]}"""]
        call["from"] = call_from
        call["to"] = call_to
        call["count"] = call.get("count", 0)
        return call
    except AttributeError as e:
        return None # only happens for bootstrap calls


def trace(frame, event, _):
    """
    Handle a trace event.
    """
    if event == "call":
        frames.append(frame)
    return trace


def start_tracing():
    threading.setprofile(trace)
    sys.setprofile(trace)


def stop_tracing():
    threading.setprofile(None)
    sys.setprofile(None)


def start_server():
    ServerThread().start()
    webbrowser.open(f"http://localhost:{PORT}")


def wait_for_client():
    print("Pynsights: waiting for client to connect...")
    while not alive:
        time.sleep(0.1)
    print("Pynsights: client connected.")


start_server()
wait_for_client()
start_tracing()
