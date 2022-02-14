#!/usr/bin/env python3

import sys
from .types import *
from .parser import parse
from .printer import print_sum, print_custom, print_csv, get_fields
from .misc import parser_error
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
        Read the timesheet data from FILE rather than from stdin. This
        option may be specified multiple times to parse data from more
        than one file. If multiple files are specified, each file will
        be parsed independently, which affects the resolution of task
        references and default attributes. The resulting data will be
        aggregated across all files, however.
    --undefined STRING
        Use the specified STRING for fields that do not have a
        defined value. Default: 'undefined' with the print command
        or the empty string with select.
    -i, --implicit-tasks
        Usually, tasks need to be defined explicitly before they can
        be referenced in time entries. While this is useful to guard
        against typos in task references, sometimes it may be useful
        to parse incomplete timesheets that are still missing some task
        definitions. If --implicit-tasks is set, the first reference to
        an undefined task will be treated as an implicit definition of
        said task, thus allowing to parse timesheets that are missing
        some or all task definitions. Implicitly defined tasks can not
        have any attributes.
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

def main() -> int:
    all_opts, rest = getopt(sys.argv[1:], "hf:i", ["help", "file=",
                            "undefined=", "implicit-tasks"])
    short2long = { "-h": "--help", "-f": "--file", "-i": "--implicit-tasks" }
    opts = { short2long.get(k, k).lstrip('-'): v for k, v in all_opts }
    if "help" in opts:
        print(_cli_help)
        return 0
    if len(rest) < 1:
        print("No COMMAND specified for timesheet", file=sys.stderr)
        return 1
    if "file" in opts:
        opts["file"] = [ v for k, v in all_opts if k in ["-f", "--file"] ]
    else:
        opts["file"] = [ "-" ]
    command, args = rest[0], rest[1:]
    if command in ["sum", "fields"] and args:
        print(f"Command '{command}' takes no further arguments",
              file=sys.stderr)
        return 1
    elif command in ["select", "print"] and not args:
        print("At least one further argument is required with the "
             f"'{command}' command", file=sys.stderr)
        return 1
    elif command not in ["sum", "fields", "select", "print"]:
        print(f"Unknown command '{command}'", file=sys.stderr)
        return 1
    sheets: list[Sheet] = list()
    implicit_tasks = True if "implicit-tasks" in opts else False
    for filename in opts['file']:
        parser_filename = None if len(opts['file']) == 1 else filename
        try:
            if filename == "-":
                sheets.append(parse(sys.stdin.read(),
                                    implicit_tasks=implicit_tasks,
                                    filename=parser_filename))
            else:
                with open(filename) as f:
                    sheets.append(parse(f.read(),
                                        implicit_tasks=implicit_tasks,
                                        filename=parser_filename))
        except ParseError as e:
            parser_error(e.filename, e.line, e.msg, context=e.context)
            return 1
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
        print('\n'.join(get_fields(sheets)))
    else:
        print(f"Unknown command '{command}'", file=sys.stderr)
        return 1
