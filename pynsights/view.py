"""
    Trace modules, classes, methods, and functions and send events to JavaScript client.
"""

import json
import os
import sys
import webbrowser

EVENT_MODULE = 0
EVENT_CALLSITE = 1
EVENT_CALL = 2
EVENT_TIMESTAMP = 3

modulenames = []
callsites = []
calls = []
duration = 0

dump_filename = None
index_output_filename = None
index_input_filename = __file__.replace("view.py", "index.html")

def read_dump():
    with open(dump_filename) as fp:
        for line in fp.readlines():
            try:
                handle_line(line)
            except Exception as e:
                raise e

def handle_line(line):
    global duration
    items = line[:-1].split()
    kind = int(items[0])
    if kind == EVENT_MODULE:
        _, parent, module = items
        modulenames.append((parent, module))
    elif kind == EVENT_CALLSITE:
        callsite = int(items[1]), int(items[2])
        callsites.append(callsite)
    elif kind == EVENT_CALL:
        when, callsite = int(items[1]), int(items[2])
        calls.append((when, callsite))
        duration = when

def open_ui():
    with open(index_input_filename) as fin:
        html = fin.read() \
            .replace("/*DURATION*/", str(duration) + " //") \
            .replace("/*MODULENAMES*/", json.dumps(modulenames, indent=4) + " //") \
            .replace("/*CALLSITES*/", json.dumps(callsites) + " //") \
            .replace("/*CALLS*/", json.dumps(calls) + " //")
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