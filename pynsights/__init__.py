"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import inspect
import threading
import traceback
import time
import collections
import asyncio
import json
import os
import sys
import webbrowser
import websockets
import queue

MY_NAME = "pynsights"
SOCKET_PORT = 8974
TRACER_MODULE_NAME = "tracer"
CALL_BUFFER_TIME = 0.3

codes = collections.defaultdict(dict)
frames = queue.Queue()
calls = []
alive = False
modules = {}


def run_server_thread():
    """
    Create the socket server in a background thread.
    """
    html = os.path.abspath(os.path.dirname(__file__))
    webbrowser.open("file://%s/pynsights.html" % html)
    asyncio.run(start_server())

async def handle_message(websocket, _path):
    """
    Process the first message received from the visualization client.
    After that, send calls
    """
    global alive, calls
    alive = True
    last_send_time = time.time()
    while True:
        call = convert_frame(frames.get())
        if call:
            calls.append(call)
        now = time.time()
        if not calls or now - last_send_time < CALL_BUFFER_TIME:
            continue
        await websocket.send(json.dumps(calls))
        calls = []
        last_send_time = now

async def start_server():
    """
    Start the socket server.
    """
    async with websockets.serve(handle_message, "localhost", SOCKET_PORT):
        await asyncio.Future()  # run forever

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
        frames.put(frame)
    return trace

def start_tracing():
    threading.setprofile(trace)
    sys.setprofile(trace)


def stop_tracing():
    threading.setprofile(None)
    sys.setprofile(None)


threading.Thread(target = run_server_thread).start()
print("Pynsights: waiting for client to connect...")
while not alive:
    time.sleep(0.1)
print("Pynsights: client connected.")
start_tracing()
