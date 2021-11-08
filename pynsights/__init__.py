"""
Record inter-module calls and save events in a file
"""

import sys
import threading
import time
import atexit
import re
import os
import inspect

caller = inspect.stack()[-1]
caller_module = caller.filename.replace(".py", "")

output_filename = "%s/pynsights_trace_%s.txt" % (os.path.expanduser('~'), caller_module)
output = None
filename_index = {}
callsite_index = {}
lock = threading.Lock()
buffer = []
MAX_BUFFER_SIZE = 1000
call_count = 0
PATHSEP = re.compile(r"[/\\]")
start = time.time()
last_flush = 0
FLUSH_INTERVAL = 1.0

EVENT_MODULE = 0
EVENT_CALLSITE = 1
EVENT_CALL = 2

def get_module(frame):
    filename = frame.f_code.co_filename
    if not filename in filename_index:
        record("%s %s\n" % (
            EVENT_MODULE,
            get_module_name(filename)))
        filename_index[filename] = len(filename_index)
    return filename_index[filename]

def get_callsite(source, target):
    callsite = "%s>%s" % (source, target)
    if not callsite in callsite_index:
        record("%s %s %s\n" % (
            EVENT_CALLSITE,
            source,
            target))
        callsite_index[callsite] = len(callsite_index)
    return callsite_index[callsite]

def get_module_name(filename):
    parts = re.split(PATHSEP, filename)
    if len(parts) == 1:
        basename = parts[0].replace(".py", "")
        if basename.startswith("<frozen "):
            parts = ["bootstrap", parts[0].replace("<frozen ", "").replace(">", "")]
        else:
            parts = [parts[0], parts[0]]
    return "%s %s" % (parts[-2], parts[-1])

def extract_call(frame):
    source = get_module(frame)
    target = get_module(frame.f_back)
    if source == target:
        raise AttributeError("ignore self calls")
    return source, target

def flush():
    global buffer
    lines, buffer = buffer, []
    for line in lines:
        output.write(line)
    output.flush()

def record(line):
    buffer.append(line)

def trace(frame, event, _):
    global call_count, last_flush
    try:
        if event == "call":
            source, target = extract_call(frame)
            now = time.time()
            when = round((now - start) * 1000)
            record("%s %s %s\n" % (EVENT_CALL, when, get_callsite(source, target)))
            call_count += 1
            if now - last_flush > FLUSH_INTERVAL:
                flush()
                last_flush = now

    except AttributeError:
        pass # happens for bootstrap calls only
    except:
        import traceback
        traceback.print_exc()
    finally:
        return trace

def start_tracing():
    global output
    output = open(output_filename, "w")
    print("Pynsights: tracing started. See", output_filename)
    threading.setprofile(trace)
    sys.setprofile(trace)

def stop_tracing():
    threading.setprofile(None)
    sys.setprofile(None)
    flush()
    print("Pynsights: tracing finished. Traced %d calls. See" % call_count, output_filename)


class Recorder(object):
    def __init__(self, file=None):
        global output_filename
        if file:
            output_filename = os.path.expanduser(file)

    def __enter__(self):
        start_tracing()

    def __exit__(self):
        stop_tracing()


atexit.register(stop_tracing)
