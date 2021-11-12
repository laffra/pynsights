"""
Record inter-module calls and save events in a file
"""

import atexit
import inspect
import functools
import os
import re
import sys
import threading
import time
import psutil

from .constants import *

process = psutil.Process(os.getpid())
caller = inspect.stack()[-1]
caller_module = caller[1].replace(".py", "")

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
CPU_INTERVAL = 0.5
tracing = False
metrics_monitor = None



def getcpu():
    cpu_count = psutil.cpu_count()
    return process.cpu_percent() / cpu_count, psutil.cpu_percent()


class SkipCall(Exception):
    pass


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
        basename = parts[0]
        if basename.startswith("<frozen "):
            parts = ["bootstrap", parts[0].replace("<frozen ", "").replace(">", "")]
        else:
            parts = [parts[0], parts[0]]
    group = parts[-2].replace(".py", "")
    module = parts[-1].replace(".py", "")
    if group == "pynsights" and module == "__init__":
        raise SkipCall("skip pynsights calls")
    return "%s %s" % (group, module)

def extract_call(frame):
    target = get_module(frame)
    source = get_module(frame.f_back)
    if source == target:
        raise SkipCall("ignore self calls")
    return source, target

def flush():
    global buffer
    lines, buffer = buffer, []
    for line in lines:
        output.write(line)
    output.flush()

def record(line):
    buffer.append(line)

def process_call(frame, event, _):
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
    except SkipCall:
        pass # not an interesting call
    except:
        import traceback
        traceback.print_exc()
    finally:
        return process_call


def measure_cpu(when):
    my_cpu, system_cpu = getcpu()
    record("%s %s %.1f %.1f\n" % (EVENT_CPU, when, my_cpu, system_cpu))


def measure_memory(when):
    memory = psutil.virtual_memory().used
    record("%s %s %.1f\n" % (EVENT_MEMORY, when, memory))


def generate_metrics():
    while tracing:
        when = round((time.time() - start) * 1000)
        measure_memory(when)
        measure_cpu(when)
        time.sleep(CPU_INTERVAL)


def start_metrics_monitor():
    global metrics_monitor
    if not metrics_monitor:
        metrics_monitor = threading.Thread(target=generate_metrics)
    metrics_monitor.start()


def start_tracing():
    global output, tracing
    tracing = True
    output = open(output_filename, "w")
    print("Pynsights: tracing started. See", output_filename)
    start_metrics_monitor()
    threading.setprofile(process_call)
    sys.setprofile(process_call)


def stop_tracing():
    global output, tracing
    tracing = False
    threading.setprofile(None)
    sys.setprofile(None)
    if buffer and output:
        flush()
        print("Pynsights: tracing finished. Traced %d calls. See" % call_count, output_filename)
        output = None


def annotate(message, event=EVENT_ANNOTATE):
    now = time.time()
    when = round((now - start) * 1000)
    record("%s %s %s\n" % (event, when, message))


def annotate_enter(func):
    annotate(str(func), EVENT_ENTER)


def annotate_exit(func):
    annotate(str(func), EVENT_EXIT)


def trace(func):
    """Decorates a function to record its execution."""

    @functools.wraps(func)
    def tracefunc_closure(*args, **kwargs):
        method = "%s.%s" % (func.__module__, func.__name__)
        annotate_enter(method)
        result = func(*args, **kwargs)
        annotate_exit(method)
        return result

    return tracefunc_closure

class Recorder(object):
    def __init__(self, file=None):
        global output_filename
        if file:
            output_filename = os.path.expanduser(file)

    def __enter__(self):
        start_tracing()

    def __exit__(self, type, value, traceback):
        stop_tracing()


atexit.register(stop_tracing)
