#!/usr/bin/env python3

import sys
from textwrap import wrap
from timesheet_types import *
from timesheet_parser import parse
from timesheet_printer import \
    print_sum, print_hours_only, print_hours_only_novat, print_custom

if __name__ == "__main__":
    try:
        log: Log = parse(sys.stdin.read())
    except ParseError as e:
        print(
            '\n'.join(wrap(f'Error while parsing line {e.line+1}: {e}')),
            file=sys.stderr
        )
        if e.context != None:
            print(e.context, file=sys.stderr, end="")
        exit(1)
    if sys.argv[1] == "sum":
        print(print_sum(log))
    elif sys.argv[1] == "hours_only":
        print(print_hours_only(log))
    elif sys.argv[1] == "hours_only_novat":
        print(print_hours_only_novat(log))
    elif sys.argv[1] == "print":
        print(print_custom(log, sys.argv[2], undefined="undefined"))
    elif sys.argv[1] in ("fields"):
        # Print all fields that can be used for format strings
        print('\n'.join(log.get_fields()))
    else:
        print(f"Unknown command '{sys.argv[1]}'", file=sys.stderr)
        exit(1)
