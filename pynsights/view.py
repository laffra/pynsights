"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import json
import sys
import webbrowser
import collections

EVENT_MODULE = 0
EVENT_CALLSITE = 1
EVENT_CALL = 2
EVENT_ANNOTATE = 3
EVENT_ENTER = 4
EVENT_EXIT = 5

modulenames = []
callsites = []
calls = []
annotations = []
duration = 0

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
            if n % one_percent == 0:
                if done % 10 == 0:
                    print("%d%% done" % done)
                done += 1

lastCall = {}

def addCall(when, callsite):
    if callsite in lastCall:
        lastWhen, count = lastCall[callsite]
        if when - lastWhen > 500:
            calls.append((lastWhen, callsite, count))
    lastCall[callsite] = when, 1

def handle_line(line):
    global duration
    items = line[:-1].split()
    kind = int(items[0])
    if kind == EVENT_MODULE:
        _, parent, module = items
        if module == "__init__":
            module = parent
        modulenames.append((parent, module))
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
    elif kind == EVENT_ENTER:
        when, message = int(items[1]), " ".join(items[2:])
        annotations.append((when, "Enter %s" % message))
        duration = when
    elif kind == EVENT_EXIT:
        when, message = int(items[1]), " ".join(items[2:])
        annotations.append((when, "Exit %s" % message))
        duration = when


def open_ui():
    with open(index_input_filename) as fin:
        html = fin.read() \
            .replace("/*DURATION*/", str(duration) + " //") \
            .replace("/*MODULENAMES*/", json.dumps(modulenames, indent=4) + " //") \
            .replace("/*CALLSITES*/", json.dumps(callsites) + " //") \
            .replace("/*CALLS*/", json.dumps(calls) + " //") \
            .replace("/*ANNOTATIONS*/", json.dumps(annotations, indent=4) + " //")
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