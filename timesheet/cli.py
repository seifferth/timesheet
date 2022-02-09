#!/usr/bin/env python3

import sys
from common_types import *
from parser import parse
from printer import print_sum, print_custom, print_csv
from misc import parser_error

if __name__ == "__main__":
    try:
        sheet: Sheet = parse(sys.stdin.read())
    except ParseError as e:
        parser_error(e.line, e.msg, context=e.context)
        exit(1)
    if sys.argv[1] == "sum":
        print(print_sum(sheet), end="")
    elif sys.argv[1] == "print":
        print(print_custom(sheet, sys.argv[2], undefined="undefined"), end="")
    elif sys.argv[1] in ("fields"):
        # Print all fields that can be used for format strings
        print('\n'.join(sheet.get_fields()))
    elif sys.argv[1] == "select":
        fields = "".join(sys.argv[2:]).split(",")
        print(print_csv(sheet, fields), end="")
    else:
        print(f"Unknown command '{sys.argv[1]}'", file=sys.stderr)
        exit(1)
