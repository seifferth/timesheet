#!/usr/bin/env python3

import sys
from common_types import *
from parser import parse
from printer import print_sum, print_custom, print_csv
from misc import parser_error
from getopt import gnu_getopt as getopt

_cli_help = """
Usage: timesheet [OPTION]... COMMAND [ARG]...

Commands
    sum         Print a summary of per-task totals for each day
                in the timesheet.
    select      Print a csv-list containing selected fields. The
                fields can be specified as command arguments and
                must be separated by commas. Whitespace around the
                commas is optional. E. g. 'select date, task, hours'.
                The wildcard '*' may be used to select all fields
                that appear in the timesheet data at least once.
    print       Like select, but takes a python format-string as a
                command argument and returns custom rather than csv
                formatted output. E. g. 'print "On {date} I worked
                {hours:.2f} hours on {task}"'. Each format string
                must be passed as a single command argument. If more
                than one format string are provided, they will be
                applied in order of specification. This may be handy
                if one wants to add a sum row showing some sort of
                total, for instance.
    fields      Print a list of fields that are available to the
                select and print commands. The available fields are
                a union of standard and custom fields. Custom fields
                are available if found in the timesheet data.

Common Options
    -f FILE, --file FILE
        Read the timesheet data from FILE rather than from stdin.
    --undefined STRING
        Use the specified STRING for fields that do not have a
        defined value. Default: 'undefined' with the print command
        or the empty string with select.
    -h, --help
        Print this help message and exit.

Standard Fields
    date, year, month, day
        The date of a certain entry, or only the day, month or year
        part of that date respectively.
    task, desc
        The task id and task description. The desc field is not
        strictly required, but it is advised to include one in
        task definitions. If the desc field is provided, it will
        be displayed in the output of the 'sum' command.
    hours, minutes
        The cumulative time spent on whatever else is selected.
        Both fields return the total value. I. e. minutes may be
        more than 60 and hours may contain fractional parts. Time
        is tracked in minutes internally. Hours can possibly be
        inaccurate due to rounding errors.
    start, stop
        The precise start and stop time of time entries. Note that
        deduplication still takes place even when start and stop
        are selected. Hence the hours and minutes are not always
        the difference between start and stop times, but rather
        the sum of this difference for all entries that share the
        same start and stop times.
""".lstrip()

if __name__ == "__main__":
    all_opts, rest = getopt(sys.argv[1:], "hf:", ["help", "file=",
                            "undefined="])
    short2long = { "-h": "--help", "-f": "--file" }
    opts = { short2long.get(k, k).lstrip('-'): v for k, v in all_opts }
    if "help" in opts:
        print(_cli_help)
        exit(0)
    if len(rest) < 1:
        print("No COMMAND specified for timesheet", file=sys.stderr)
        exit(1)
    if "file" in opts:
        opts["file"] = [ v for k, v in all_opts if k in ["-f", "--file"] ]
    else:
        opts["file"] = [ "-" ]
    command, args = rest[0], rest[1:]
    if command in ["sum", "fields"] and args:
        print(f"Command '{command}' takes no further arguments",
              file=sys.stderr)
        exit(1)
    elif command in ["select", "print"] and not args:
        print("At least one further argument is required with the "
             f"'{command}' command", file=sys.stderr)
        exit(1)
    elif command not in ["sum", "fields", "select", "print"]:
        print(f"Unknown command '{command}'", file=sys.stderr)
        exit(1)
    sheets: list[Sheet] = list()
    for filename in opts['file']:
        try:
            if filename == "-":
                sheets.append(parse(sys.stdin.read()))
            else:
                with open(filename) as f:
                    sheets.append(parse(f.read()))
        except ParseError as e:
            parser_error(e.line, e.msg, context=e.context)
            exit(1)
    if command == "sum":
        print(print_sum(sheets), end="")
    elif command == "select":
        fields = [ f.strip() for f in " ".join(args).split(",") ]
        undefined = opts.get("undefined", "")
        print(print_csv(sheets, fields, undefined=undefined), end="")
    elif command == "print":
        undefined = opts.get("undefined", "undefined")
        for fstring in args:
            print(print_custom(sheets, fstring, undefined=undefined),
                  end="")
    elif command == "fields":
        for sheet in sheets:
            print('\n'.join(sheet.get_fields()))
    else:
        print(f"Unknown command '{command}'", file=sys.stderr)
        exit(1)
