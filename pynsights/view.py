"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import json
import sys
import webbrowser
from constants import *

modulenames = []
typenames = []
callsites = []
calls = []
cpus = []
heap = []
gcs = []
memories = []
annotations = []
duration = 0
lastCall = {}
when = 0

dump_filename = None
index_output_filename = None
index_input_filename = __file__.replace("view.py", "index.html")


def read_dump():
    done = 0
    with open(dump_filename) as fp:
        lines = fp.readlines()
        one_percent = round(len(lines) / 100)
        for n, line in enumerate(lines):
            handle_line(line)
            if not one_percent or n % one_percent == 0:
                if done % 10 == 0:
                    print("%d%% done" % done)
                done += 1
        flushCallSites()

def flushCallSites():
    for callsite in lastCall:
        when, count = lastCall[callsite]
        calls.append((when, callsite, count))
    lastCall.clear()

def addCall(when, callsite):
    count = 0
    if callsite in lastCall:
        lastWhen, count = lastCall[callsite]
        if when - lastWhen > 500:
            calls.append((lastWhen, callsite, count))
    lastCall[callsite] = when, count + 1

def handle_line(line):
    global duration, when
    items = line[:-1].split()
    kind = int(items[0])
    if kind == EVENT_MODULE:
        _, parent, module = items
        if module == "__init__":
            module = parent
        modulenames.append((parent, module))
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
        addCall(when, callsite)
        duration = when
    elif kind == EVENT_ANNOTATE:
        message = " ".join(items[1:])
        annotations.append((when, message))
        duration = when
        flushCallSites()
    elif kind == EVENT_ENTER:
        message = " ".join(items[1:])
        annotations.append((when, "Enter %s" % message))
        duration = when
        flushCallSites()
    elif kind == EVENT_EXIT:
        message = " ".join(items[1:])
        annotations.append((when, "Exit %s" % message))
        duration = when
        flushCallSites()
    elif kind == EVENT_TIMESTAMP:
        when = int(items[1])


def open_ui():
    with open(index_input_filename) as fin:
        html = fin.read() \
            .replace("/*DURATION*/", str(duration) + " //") \
            .replace("/*MODULENAMES*/", json.dumps(modulenames, indent=4) + " //") \
            .replace("/*CALLSITES*/", json.dumps(callsites) + " //") \
            .replace("/*CALLS*/", json.dumps(calls) + " //") \
            .replace("/*CPUS*/", json.dumps(cpus) + " //") \
            .replace("/*ANNOTATIONS*/", json.dumps(annotations) + " //") \
            .replace("/*HEAP*/", "[\n    " + ",\n    ".join(json.dumps(snapshot) for snapshot in heap) + "\n] //") \
            .replace("/*GC*/", "[\n    " + ",\n    ".join(json.dumps(gc) for gc in gcs) + "\n] //") \
            .replace("/*TYPES*/", json.dumps(typenames) + " //") \
            .replace("/*MEMORIES*/", json.dumps(memories, indent=4) + " //")
        with open(index_output_filename, "w") as fout:
            fout.write(html)
        print("Opening", index_output_filename)
        webbrowser.open("file://" + index_output_filename)


def main():
    global dump_filename
    global index_output_filename
    if len(sys.argv) != 2:
        print("Usage: view <path-to-pynsights-trace-file>")
    else:
        dump_filename = sys.argv[1]
        index_output_filename = dump_filename.replace(".txt", ".html")
        read_dump()
        if calls:
            open_ui()
        else:
            print("Error: no calls collected")


if __name__ == "__main__":
    main()