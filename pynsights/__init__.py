"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import inspect
import threading
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

def extract_details(frame):
    return {
        "codename": frame.f_code.co_name,
        "locals": [f"${key}=${safe_repr(value)}" for key,value in frame.f_locals.items()],
        "filename": frame.f_code.co_filename,
        "lineno": frame.f_code.co_firstlineno,
        "module": inspect.getmodule(frame).__name__,
    }

def is_bootstrap_call(frame):
    while frame:
        if not inspect.getmodule(frame):
            return True
        frame = frame.f_back
    return False

def trace(frame, event, _):
    """
    Handle a trace event.
    """
    try:
        if event != "call" or not frame or not frame.f_back or is_bootstrap_call(frame):
            return trace
        call_to = extract_details(frame)
        call_from = extract_details(frame.f_back)
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
        print(e)
    finally:
        return trace

def start_tracing():
    threading.settrace(trace)
    sys.settrace(trace)


def stop_tracing():
    threading.settrace(None)
    sys.settrace(None)


threading.Thread(target = run_server_thread).start()
print("Pynsights: waiting for client to connect...")
while not alive:
    time.sleep(0.1)
print("Pynsights: client connected.")
start_tracing()
