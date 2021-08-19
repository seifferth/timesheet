#!/usr/bin/env python3

import re, sys
from decimal import Decimal
from timesheet_types import *

def parse_day(date: str, lines: list[str], log: Log) -> None:
    d = Day(date)
    times: dict[Task,Decimal] = dict()
    global_start: Time = None
    last_start: Time = None
    for lno, l in enumerate(lines):
        if re.match(r'^[^0-9\s]', l):       # Attribute line
            raise ParseError(lno, 'Continuation lines for time level '\
                              'overrides are not implemented yet')
        elif re.match(r'^[0-9]', l):        # Time entry
            try:
                time, entry_type, *l = l.split(maxsplit=2)
            except:
                raise ParseError(lno, 'Unable to parse time entry')
            time = Time(time)
            l = None if len(l) == 0 else l[0]
            if entry_type == "stop":
                if global_start == None: raise ParseError(lno,
                    "Cannot stop time entry without starting it first"
                )
                # TODO: Use global start for double-checking
                times[task] += time.decimal() - last_start.decimal()
                global_start = None
                last_start = None
            elif entry_type == "start" and l == None:
                if not global_start == None: raise ParseError(lno,
                    "Cannot create an initial start time without stopping "\
                    "the last count first"
                )
                global_start = time
                continue
            elif entry_type == "start":
                if global_start == None: global_start = time
                if last_start != None:
                    times[task] += time.decimal() - last_start.decimal()
                task, *l = l.split(maxsplit=1)
                l = None if len(l) == 0 else l[0]
                try:
                    task = log.get_task(task)
                except ParseError as e:
                    raise ParseError(lno, e.msg)
                if l:       # TODO: Add support for multiple overrides
                    key, val = re.split(r'\s*=\s', l, maxsplit=1)
                    if key == "desc":           task = task.copy(desc=val)
                    elif key == "rate":         task = task.copy(rate=val)
                    elif key == "vat":          task = task.copy(vat=val)
                    else:
                        task = task.copy()
                        task.other[key] = val
                if task not in times.keys(): times[task] = Decimal(0)
                last_start = time
            else:
                raise ParseError(lno,
                    f"Unknown time entry type '{entry_type}'"
                )
    d.add_times(times)
    log.add_day(d)

def parse_task(lines: list[str], log: Log) -> None:
    name, l = lines[0].split(maxsplit=1)
    t = Task(name)
    for l in [l, *lines[1:]]:
        if not "=" in l:
            raise ParseError(0,
                f"Expected task attribute of form 'name = val' but found '{l}'"
            )
        key, val = re.split(r'\s*=\s*', l, maxsplit=1)
        if key == "desc":       t.set_desc(val)
        elif key == "rate":     t.set_rate(val)
        elif key == "vat":      t.set_vat(val)
        else:                   t.set_other(key, val)
    log.add_task(t)

def parse_default(lines: list[str], log: Log) -> None:
    for l in lines:
        key, val = re.split(r'\s*=\s', l, maxsplit=1)
        if key == "rate":  log.set_default_rate(val)
        elif key == "vat": log.set_default_vat(val)
        else: raise ParseError(0, f"Unknown default value '{key}'")

def strip_comments(log: str) -> str:
    """Strips comments and trailing whitespace"""
    log = re.sub(r'^#.*$', '', log, flags=re.M)
    log = re.sub(r'\s+#.*$', '', log, flags=re.M)
    log = re.sub(r'^\s+$', '', log, flags=re.M)
    return log

def starts_blank(line: str) -> bool:
    return bool(re.match(r'^\s', line, flags=re.M))
    #return bool(line[0].strip())

def parse(log: str) -> Log:
    res = Log()
    lines: list[str] = strip_comments(log).splitlines()
    i: int = 0
    try:
        while i < len(lines):
            l = lines[i]
            if not l.strip():       i+=1; continue
            if starts_blank(l):
                raise ParseError(i, "Unexpected indent")
            entry_type, *l = l.split(maxsplit=1)

            ls = [] if len(l) == 0 else [l[0]]; j=i+1
            while j < len(lines) and starts_blank(lines[j]):
                ls.append(lines[j].lstrip()); j+=1
            # Join continuation lines
            cl = 0
            while cl < len(ls):
                if len(ls[cl]) > 0 and ls[cl][-1] == '\\':
                    if cl+1 >= len(ls):
                        i+=cl; raise ParseError(0, 'Unexpected end of block')
                    ls[cl] = ls[cl][:-1] + ls[cl+1].lstrip()
                    del ls[cl+1]
                else: cl+=1
            if entry_type == "default":
                parse_default(ls, res)
            elif entry_type == "task":
                parse_task(ls, res)
            elif re.match(r'^[0-9]', entry_type):
                if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', entry_type):
                    raise ParseError(0, f"Cannot parse date '{entry_type}'")
                parse_day(date=entry_type, lines=ls, log=res)
            else:
                raise ParseError(0, f"Unknown entry type '{entry_type}'")
            i=j; continue
        return res
    except ParseError as e:
        lno = e.line+i+1
        pre = lines[max(0,lno-2):lno]
        if pre: pre = list(map(lambda x: f'  | {x}', pre))
        post = lines[min(len(lines),lno+1):min(len(lines),lno+4)]
        if post: post = list(map(lambda x: f'  | {x}', post))
        context = (('\n'.join(pre)+'\n') if pre else "") + \
                  f'  > {lines[lno]}\n' + \
                  (('\n'.join(post)+'\n') if post else "")
        raise ParseError(lno, e.msg, context=context) from e
