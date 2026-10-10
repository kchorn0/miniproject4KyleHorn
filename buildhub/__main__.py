# INF601 - Advanced Programming in Python
# Kyle Horn
# Mini Project 4
"""buildhub command-line interface. Usage:

    python -m buildhub summarize <file> --group-by G --value V --agg A [--decimals D]
    python -m buildhub top <file> --key K --n N
"""
import argparse  # standard-library tool that reads command-line options like --key
import sys  # gives us sys.exit to hand main()'s return code back to the shell

from buildhub import datakit  # our five functions live here


def build_parser():
    """Describe the two subcommands and their options for argparse."""
    # The top-level parser: "python -m buildhub ..."
    parser = argparse.ArgumentParser(prog="python -m buildhub", description="Tiny data toolkit")
    # Subcommands; required=True means running with no subcommand prints an error
    sub = parser.add_subparsers(dest="command", required=True)

    # --- python -m buildhub summarize <file> --group-by G --value V --agg A [--decimals D]
    s = sub.add_parser("summarize", help="group rows and aggregate a numeric field")
    s.add_argument("file", help="path to a .csv or .json file")  # positional: the data file
    s.add_argument("--group-by", required=True, help="field to group by")  # becomes args.group_by
    s.add_argument("--value", required=True, help="numeric field to aggregate")
    # choices makes argparse reject a bad --agg with a clear message before any work happens
    s.add_argument("--agg", required=True, choices=sorted(datakit.AGGREGATES))
    # type=int turns the text "2" into the number 2; default matches summarize()'s default
    s.add_argument("--decimals", type=int, default=2, help="decimal places for mean (default 2)")

    # --- python -m buildhub top <file> --key K --n N
    t = sub.add_parser("top", help="show the N rows with the largest numeric key")
    t.add_argument("file", help="path to a .csv or .json file")
    t.add_argument("--key", required=True, help="numeric field to rank by")
    t.add_argument("--n", type=int, required=True, help="how many rows to show")  # text -> int
    return parser


def main(argv=None):
    # argv=None makes argparse read the real command line; tests can pass a list instead
    args = build_parser().parse_args(argv)
    try:
        # Both subcommands start by loading the file into a list of dict rows
        records = datakit.load_records(args.file)

        if args.command == "summarize":
            # Aggregate, then print the sorted "key: value" text report
            summary = datakit.summarize(records, args.group_by, args.value, args.agg, args.decimals)
            print(datakit.to_report(summary))
        else:  # args.command == "top" (argparse only allows these two)
            # Print each of the top rows on its own line, as a Python dict
            for row in datakit.top_n(records, args.key, args.n):
                print(row)
    except KeyError as e:
        # A field name that isn't in the data (e.g. --key pointz); e.args[0] is the missing name
        print(f"error: field {e.args[0]!r} not found in {args.file}", file=sys.stderr)
        return 1  # non-zero exit code tells the shell the command failed
    except (ValueError, OSError) as e:
        # ValueError: wrong file type or a non-numeric value; OSError: file missing/unreadable.
        # Print one short line to stderr (the error stream) instead of a long traceback.
        print(f"error: {e}", file=sys.stderr)
        return 1  # non-zero exit code tells the shell the command failed
    # 0 is the shell's code for "success"
    return 0


if __name__ == "__main__":
    sys.exit(main())
