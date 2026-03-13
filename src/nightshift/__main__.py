"""CLI entry point: python -m nightshift [run|collect|draft]"""

from __future__ import annotations

import argparse
import asyncio
import sys

from nightshift.config import load_settings, load_style
from nightshift import pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nightshift",
        description="Automated overnight content pipeline",
    )
    parser.add_argument(
        "command",
        choices=["run", "collect", "draft"],
        nargs="?",
        default="run",
        help="Pipeline command (default: run)",
    )
    args = parser.parse_args()

    settings = load_settings()
    style = load_style()

    match args.command:
        case "collect":
            items = asyncio.run(pipeline.collect(settings))
            for item in items:
                print(f"[{item.source}] {item.title} ({item.score})")
                print(f"  {item.url}\n")

        case "draft":
            items = asyncio.run(pipeline.collect(settings))
            digest = asyncio.run(pipeline.draft(settings, style, items))
            print(digest.summary)

        case "run":
            asyncio.run(pipeline.run(settings, style))

        case _:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
