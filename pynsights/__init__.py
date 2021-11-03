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

MY_NAME = "pynsights"
SOCKET_PORT = 8974
TRACER_MODULE_NAME = "tracer"

codes = collections.defaultdict(dict)
events = []
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
    Process a message received from the visualization client.
    """
    global events, alive
    async for message in websocket:
        alive = True
        if message == "events":
            data, events = events, []
            await websocket.send(json.dumps(data))

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

def trace(frame, event, _):
    """
    Handle a trace event.
    """
    try:
        if event != "call" and event != "c_call" :
            return trace
        try:
            call_to = extract_details(frame)
            call_from = extract_details(frame.f_back)
        except AttributeError as e:
            # this happens only for bootstrap calls
            return
        if call_to["module"] == call_from["module"]:
            return trace
        call = codes[f"""
            {call_to["filename"]}
            {call_to["lineno"]}
            {call_from["filename"]}
            {call_from["lineno"]}
        """]
        call["from"] = call_from
        call["to"] = call_to
        call["count"] = call.get("count", 0)
        events.append(call)
    except Exception as e:
        traceback.print_exc()
    finally:
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
