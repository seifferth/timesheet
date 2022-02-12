# Timesheet – A simple yet flexible system for time tracking

Timesheets are simple text files formatted in a way that is well defined
(in order to allow automated processing of the data) yet still remains
easy to read and write by humans. `timesheet` is a command line program
for summarising, extracting and converting the data contained in such
timesheets.

The Quick-start section included below provides a very short introduction
into working with timesheet.

## Installing

This repository uses python setuptools and can be installed with pip. To
install timesheet into the current user's home directory, for instance,
you can simply invoke `pip install --user .`. Other pip arguments should
also work.

When the program is installed, a script named `timesheet` is provided with
the installation. Alternatively, it is possible to invoke the program as
`python3 -m timesheet`. This invocation also works without installing
and may be more convenient during development and testing.

There are a number of end-to-end test cases detailed in the `tests/`
directory. These test cases can be executed by running the `./test.py`
script. The test script exits with a non-zero exit code if any of the
tests fails. It also prints a summary of test results to stdout.

## Quick-start

An example timesheet may look like this:

```
task docs   # Write documentation
    desc = Create a human-readable description of the program's behaviour
    status = todo
task code   # Write code
    desc = Create a computer-readable description of a certain program's \
           behaviour
    status = done

2022-02-10  # Thursday, time to wrap up some half-baked stuff
    13:00 start docs
    14:00 start code
    14:15 stop

task research
    desc   =  Search for similar programs that may provide inspiration \
              for future work
    status =  todo
    note   =  This may actually be much more important than any other \
              kind of work you might be doing.

2022-02-11  # Friday, which is the day I like to focus on reading rather
            # than writing
    13:00 start research
    15:20 start docs
    15:30 start research
    17:00 stop      # Dinner break
    19:00 start research
    20:15 stop
```

If you save the above timesheet as `time.log`, you can query it like this:

```
$ timesheet -f time.log sum
2022-02-10
    docs Create a human-readable description of the program..  1.00
    code Create a computer-readable description of a certai..  0.25
    Total hours .............................................. 1.25

2022-02-11
    research Search for similar programs that may provide i..  5.08
    docs Create a human-readable description of the program..  0.17
    Total hours .............................................. 5.25

Grand total .................................................. 6.50
```

```
$ timesheet -f time.log print '{task:<20} {hours:.4f}'
docs                 1.1667
code                 0.2500
research             5.0833
```

```
$ timesheet -f time.log print '[{status}] {task} ({hours} hours spent)'
[todo] docs (1.17 hours spent)
[done] code (0.25 hours spent)
[todo] research (5.08 hours spent)
```

```
$ timesheet -f time.log select date,task,hours,minutes
date,task,hours,minutes
2022-02-10,docs,1.00,60
2022-02-10,code,0.25,15
2022-02-11,research,5.08,305
2022-02-11,docs,0.17,10
```

```
$ timesheet -f time.log print '{task:<10} {hours}' 'Total      {hours}'
docs       1.17
code       0.25
research   5.08
Total      6.50
```

For further command line options and a full list of fields available by
default see `timesheet -h`.

## Known Issues

- The timesheet parser's line number tracking features are a holy
  mess. They are well covered with test cases in `tests/`, though,
  so line numbers in parser error messages should hopefully still
  be correct in most cases.

## License

All files in this repository are made available under the terms of the
GNU General Purpose License, version 3 or later. A copy of that license
is included in the repository as `license.txt`.
