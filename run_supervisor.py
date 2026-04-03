#!/usr/bin/env python3
"""CLI entrypoint for running the full LatticeReAct supervisor architecture."""

import argparse
import contextlib
import io
import sys
import time

from agents.supervisor import create_supervisor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full LatticeReAct supervisor + sub-agent architecture from terminal."
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Question to ask the supervisor. If omitted, you will be prompted interactively.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Hide supervisor iteration logs and print only final answer.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.query:
        query = " ".join(args.query).strip()
    else:
        query = input("Enter your materials question: ").strip()

    if not query:
        print("Error: query cannot be empty.", file=sys.stderr)
        return 1

    try:
        supervisor = create_supervisor()

        if args.quiet:
            supervisor.verbose = False

        start = time.time()
        if args.quiet:
            with contextlib.redirect_stdout(io.StringIO()):
                result = supervisor.invoke({"input": query})
        else:
            result = supervisor.invoke({"input": query})
        elapsed = time.time() - start

        answer = result.get("output", str(result))
        print("\n" + "=" * 80)
        print("FINAL ANSWER")
        print("=" * 80)
        print(answer)
        print("=" * 80)
        print(f"Completed in {elapsed:.2f}s")
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
