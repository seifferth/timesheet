#!/usr/bin/env python3

import sys
from timesheet_types import *
from timesheet_parser import parse
from timesheet_printer import \
    print_sum, print_hours_only, print_hours_only_novat

if __name__ == "__main__":
    try:
        log: Log = parse(sys.stdin.read())
    except ParseError as e:
        print(e, file=sys.stderr, end="")
        exit(1)
    if sys.argv[1] == "sum":
        print(print_sum(log))
    elif sys.argv[1] == "hours_only":
        print(print_hours_only(log))
    elif sys.argv[1] == "hours_only_novat":
        print(print_hours_only_novat(log))
