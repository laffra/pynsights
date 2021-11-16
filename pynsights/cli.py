# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m pynsights` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `pynsights.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `pynsights.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from __future__ import annotations

import argparse
import sys
import tempfile
from contextlib import suppress
from pathlib import Path
from runpy import run_module, run_path

from pynsights import Recorder
from pynsights.view import view


def get_parser() -> argparse.ArgumentParser:
    """
    Return the program argument parser.

    Returns:
        The argument parser for the program.
    """
    usage = "%(prog)s [GLOBAL_OPTS...] COMMAND [COMMAND_OPTS...]"
    description = "Understand Python programs by visualizing how modules interact."
    parser = argparse.ArgumentParser(add_help=False, usage=usage, description=description, prog="pynsights")

    main_help = "Show this help message and exit. Commands also accept the -h/--help option."
    command_help = "Show this help message and exit."

    global_options = parser.add_argument_group(title="Global options")
    global_options.add_argument("-h", "--help", action="help", help=main_help)

    subparsers = parser.add_subparsers(dest="command", title="Commands", metavar="", prog="pynsights")

    def subparser(command: str, text: str, **kwargs) -> argparse.ArgumentParser:
        sub = subparsers.add_parser(command, add_help=False, help=text, description=text, **kwargs)
        sub.add_argument("-h", "--help", action="help", help=command_help)
        return sub

    record_parser = subparser("record", "Record the interactions within the execution of a Python program.")
    record_parser.add_argument("-o", "--output", type=Path, default=None, help="Output path of the recorded data.")
    record_parser.add_argument("record_command", nargs="+", help="The Python script/module to run and its options.")

    render_parser = subparser("render", "Render the given data file into a standalone HTML file.")
    render_parser.add_argument("-w", "--browser", "--open", dest="browser", action="store_true", help="Open the HTML file in your default browser.")
    render_parser.add_argument("input_file", type=Path, help="The input data file to render.")
    render_parser.add_argument("-o", "--output", type=Path, default=None, help="Output path of the standalone HTML.")

    run_parser = subparser("run", "Record and render in one go.")
    run_parser.add_argument("-w", "--browser", "--open", dest="browser", action="store_true", help="Open the HTML file in your default browser.")
    run_parser.add_argument("-o", "--output", type=Path, default=None, help="Output path of the final HTML file.")
    run_parser.add_argument("record_command", nargs="+", help="The Python script/module to run and its options.")

    return parser


def record(command, output=None):
    module = command[0]
    if Path(module).exists():
        runpy = run_path
    else:
        runpy = run_module
    
    sys.argv = command
    with suppress(SystemExit):
        with Recorder(output):
            runpy(module, run_name="__main__")


def render(input_file, output_file, open_browser):
    view(input_file, output_file, open_browser)


def run(command, output=None, open_browser=False):
    tmpname = Path(command[0]).stem
    with tempfile.TemporaryDirectory() as tmpdir:
        data_file = Path(tmpdir, f"{tmpname}.txt")
        record(command, output=data_file)
        render(data_file, output or f"{tmpname}.html", open_browser)


def main(args: list[str] | None = None) -> int:
    """
    Run the main program.

    This function is executed when you type `pynsights` or `python -m pynsights`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args)

    if opts.command == "record":
        record(opts.record_command, opts.output)
        return 0
    
    if opts.command == "render":
        render(opts.input_file, opts.output, opts.browser)
        return 0

    if opts.command == "run":
        run(opts.record_command, opts.output, opts.browser)
        return 0
    
    if opts.command:
        print(f"error: unknown command '{opts.command}'", file=sys.stderr)

    parser.print_help(file=sys.stderr)
    return 1
