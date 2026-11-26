"""Command-line entry point."""
import argparse
import os

from . import __version__
from .report import render_json, render_text
from .scanner import scan


def main(argv=None, env=None):
    parser = argparse.ArgumentParser(
        prog="win-disk-doctor",
        description="Show what is using space in well-known Windows cleanup locations "
        "and what is safe to clean. Read-only: nothing is deleted.",
    )
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
    arguments = parser.parse_args(argv)

    results = scan(os.environ if env is None else env)
    print(render_json(results) if arguments.json else render_text(results))
    return 0
