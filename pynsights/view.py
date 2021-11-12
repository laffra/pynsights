"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import json
import sys
import webbrowser
from constants import *

modulenames = []
callsites = []
calls = []
cpus = []
memories = []
annotations = []
duration = 0
lastCall = {}

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
    global duration
    items = line[:-1].split()
    kind = int(items[0])
    if kind == EVENT_MODULE:
        _, parent, module = items
        if module == "__init__":
            module = parent
        modulenames.append((parent, module))
    elif kind == EVENT_CPU:
        when, cpu, cpu_system = int(items[1]), float(items[2]), float(items[3])
        cpus.append((when, cpu, cpu_system))
    elif kind == EVENT_MEMORY:
        when, memory = int(items[1]), float(items[2])
        memories.append((when, memory))
    elif kind == EVENT_CALLSITE:
        callsite = int(items[1]), int(items[2])
        callsites.append(callsite)
    elif kind == EVENT_CALL:
        when, callsite = int(items[1]), int(items[2])
        addCall(when, callsite)
        duration = when
    elif kind == EVENT_ANNOTATE:
        when, message = int(items[1]), " ".join(items[2:])
        annotations.append((when, message))
        duration = when
        flushCallSites()
    elif kind == EVENT_ENTER:
        when, message = int(items[1]), " ".join(items[2:])
        annotations.append((when, "Enter %s" % message))
        duration = when
        flushCallSites()
    elif kind == EVENT_EXIT:
        when, message = int(items[1]), " ".join(items[2:])
        annotations.append((when, "Exit %s" % message))
        duration = when
        flushCallSites()


def open_ui():
    with open(index_input_filename) as fin:
        html = fin.read() \
            .replace("/*DURATION*/", str(duration) + " //") \
            .replace("/*MODULENAMES*/", json.dumps(modulenames, indent=4) + " //") \
            .replace("/*CALLSITES*/", json.dumps(callsites) + " //") \
            .replace("/*CALLS*/", json.dumps(calls) + " //") \
            .replace("/*CPUS*/", json.dumps(cpus) + " //") \
            .replace("/*ANNOTATIONS*/", json.dumps(annotations) + " //") \
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
        open_ui()


if __name__ == "__main__":
    main()