"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import json
import pathlib
import webbrowser
import os
import time
from pynsights.constants import *

modulenames = []
typenames = []
callsites = []
calls = []
total_calls = 0
cpus = []
heap = []
gcs = []
memories = []
annotations = []
duration = 0
last_call = {}
when = 0

template_file = __file__.replace("render.py", "index.html")
filler = " " * 40


def show_progress(percent, end=""):
    print(f"\r - {percent}% done - {total_calls:,} calls processed", filler, end=end)


def format_bytes(size):
    power = 2**10
    if size < power:
        return f"{size} bytes"
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size)}{power_labels[n]}B"


def read_dump(input_file):
    done = 0
    print(f"Loading {input_file}")
    print(f" - Dump size: {format_bytes(os.path.getsize(input_file))}")
    with open(input_file) as fp:
        lines = fp.readlines()
        one_percent = round(len(lines) / 100)
        for n, line in enumerate(lines):
            try:
                handle_line(line)
            except Exception as e:
                print(f"Error handling line: '{line}'")
                print(e)
            if not one_percent or n % one_percent == 0:
                show_progress(done)
                done += 1
        flush_call_sites()
    print(f"\r - Number of calls: {total_calls:,}", filler)


def flush_call_sites():
    for callsite in last_call:
        when, count = last_call[callsite]
        calls.append((when, callsite, count))
    last_call.clear()

MODULES_TO_SKIP = {
    "python.importlib",
    "pynsights",
    "pynsights.pynsights",
    "pynsights.pynsights.cli",
    "pynsights.pynsights.record",
    "python.runpy",
    "python.zipimport",
}

def skip_module(moduleIndex):
    if moduleIndex < len(modulenames):
        return modulenames[moduleIndex] in MODULES_TO_SKIP

def skip_call(callsite):
    if callsite < len(callsites):
        source, target = callsites[callsite]
        return skip_module(source) or skip_module(target)
        
def add_call(when, callsite):
    global total_calls
    if skip_call(callsite):
        return
    total_calls += 1
    count = 0
    if callsite in last_call:
        lastWhen, count = last_call[callsite]
        if when - lastWhen > 500:
            calls.append((lastWhen, callsite, count))
    last_call[callsite] = when, count + 1

def handle_line(line):
    global duration, when
    items = line[:-1].split()
    kind = int(items[0])
    if kind == EVENT_MODULE:
        _, module = items
        modulenames.append(module)
    elif kind == EVENT_CPU:
        cpu, cpu_system = float(items[1]), float(items[2])
        cpus.append((when, cpu, cpu_system))
    elif kind == EVENT_MEMORY:
        memory = float(items[1])
        memories.append((when, memory))
    elif kind == EVENT_TYPE:
        typename = items[1]
        typenames.append(typename)
    elif kind == EVENT_HEAP:
        counts = json.loads(" ".join(items[1:]))
        heap.append((when, counts))
    elif kind == EVENT_GC:
        gc_duration, collected, uncollectable = int(items[1]), int(items[2]), int(items[3])
        gcs.append((when, gc_duration, collected, uncollectable))
    elif kind == EVENT_CALLSITE:
        callsite = int(items[1]), int(items[2])
        callsites.append(callsite)
    elif kind == EVENT_CALL:
        callsite = int(items[1])
        add_call(when, callsite)
        duration = when
    elif kind == EVENT_ANNOTATE:
        message = " ".join(items[1:])
        annotations.append((when, message))
        duration = when
        flush_call_sites()
    elif kind == EVENT_ENTER:
        message = " ".join(items[1:])
        annotations.append((when, f"Enter {message}"))
        duration = when
        flush_call_sites()
    elif kind == EVENT_EXIT:
        message = " ".join(items[1:])
        annotations.append((when, f"Exit {message}"))
        duration = when
        flush_call_sites()
    elif kind == EVENT_TIMESTAMP:
        when = int(items[1])


def generate(output):
    with open(template_file) as fin:
        template = fin.read()
    html = template\
        .replace("/*DURATION*/", str(duration) + " //") \
        .replace("/*MODULENAMES*/", json.dumps(modulenames) + " //") \
        .replace("/*CALLSITES*/", json.dumps(callsites) + " //") \
        .replace("/*CALLS*/", json.dumps(calls) + " //") \
        .replace("/*CPUS*/", json.dumps(cpus) + " //") \
        .replace("/*ANNOTATIONS*/", json.dumps(annotations) + " //") \
        .replace("/*HEAP*/", "[\n    " + ",\n    ".join(json.dumps(snapshot) for snapshot in heap) + "\n] //") \
        .replace("/*GC*/", "[\n    " + ",\n    ".join(json.dumps(gc) for gc in gcs) + "\n] //") \
        .replace("/*TYPES*/", json.dumps(typenames) + " //") \
        .replace("/*MEMORIES*/", json.dumps(memories, indent=4) + " //")
    with open(output, "w") as fout:
        fout.write(html)
    print(" - Output file:", output, f"{format_bytes(os.path.getsize(output))}", filler)


def open_ui(output):
    print("Opening output now")
    webbrowser.open("file://" + str(output.resolve()))


def render(input_file, output=None, open_browser=False):
    start = time.time()
    read_dump(input_file)
    if output is None:
        output = input_file.with_suffix(".html")
    print(" - Processing time:", f"{time.time() - start:.1f}s", filler)
    start = time.time()
    generate(output)
    if open_browser:
        open_ui(pathlib.Path(output))
