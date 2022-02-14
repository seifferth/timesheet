#!/usr/bin/env python3

import re, sys
from .types import *

def parse_day(lno_offset: int, date: str, lines: list[str], sheet: Sheet,
              implicit_tasks=False) -> None:
    last_start: Time = None
    start: EntryStartPoint = None
    for lno, l in enumerate(lines):
        if re.match(r'^[^0-9\s]', l):       # Attribute line
            if not "=" in l:
                raise ParseError(lno_offset+lno,
                    "Expected time entry attribute of form "
                   f"'name = val' but found '{l}'"
                )
            key, val = re.split(r'\s*=\s*', l, maxsplit=1)
            start.attrs[key] = val
        elif re.match(r'^[0-9]', l):        # Time entry
            try:
                time, entry_type, *l = l.split(maxsplit=2)
            except:
                raise ParseError(lno_offset+lno, 'Unable to parse time entry')
            time = Time(lno_offset+lno, time)
            l = None if len(l) == 0 else l[0]
            if entry_type == "stop":
                if last_start == None: raise ParseError(lno_offset+lno,
                    "Cannot stop time entry without starting it first"
                )
                sheet.add_entry(Entry(start, time))
                last_start = None
                start = None
            elif entry_type == "start" and l == None:
                raise ParseError(lno_offset+lno,
                    "Cannot start time entry without specifying a task"
                )
            elif entry_type == "start":
                last_start = time
                if start != None:
                    sheet.add_entry(Entry(start, time))
                task, *l = l.split(maxsplit=1)
                l = None if len(l) == 0 else l[0]
                if task not in sheet.tasks.keys():
                    if implicit_tasks:
                        sheet.add_task(Task(lno_offset+lno+1, task))
                    else:
                        raise ParseError(lno_offset+lno,
                            f'Task {task} referenced before assignment'
                        )
                try:
                    start = EntryStartPoint(lno_offset+lno, task, date, time)
                except ParseError as e:
                    raise ParseError(lno_offset+lno, e.msg)
                if l:
                    if not "=" in l:
                        raise ParseError(lno_offset+lno,
                            "Expected time entry attribute of form "
                           f"'name = val' but found '{l}'"
                        )
                    key, val = re.split(r'\s*=\s*', l, maxsplit=1)
                    start.attrs[key] = val
            else:
                raise ParseError(lno_offset+lno,
                    f"Unknown time entry type '{entry_type}'"
                )
    if start != None:
        raise ParseError(start.lno, "Missing stop time")

def parse_task(lno: int, lines: list[str], sheet: Sheet) -> None:
    name, *l = lines[0].split(maxsplit=1)
    ls_offset = -1 if l else 0
    t = Task(lno, name)
    for i, l in enumerate(l + lines[1:]):
        if not l.strip(): continue
        if not "=" in l:
            raise ParseError(lno+i+ls_offset,
                f"Expected task attribute of form 'name = val' but found '{l}'"
            )
        key, val = re.split(r'\s*=\s*', l, maxsplit=1)
        t.set(key, val)
    sheet.add_task(t)

def parse_default(lno: int, lines: list[str], sheet: Sheet) -> None:
    for i, l in enumerate(lines):
        if not l.strip(): continue
        if not "=" in l:
            raise ParseError(lno+i, "Expected default attribute of form "
                            f"'name = val' but found '{l}'")
        key, val = re.split(r'\s*=\s*', l, maxsplit=1)
        sheet.set_default(key, val, lno=lno+i)

def strip_comments(sheet: str) -> str:
    """Strips comments"""
    sheet = re.sub(r'^#.*$', '', sheet, flags=re.M)
    sheet = re.sub(r'[^\n\S]+#.*$', r'', sheet, flags=re.M)
    return sheet

def starts_blank(line: str) -> bool:
    if not line.strip(): return True
    return bool(re.match(r'^\s', line))

def parse(sheet: str, implicit_tasks=False) -> Sheet:
    res = Sheet()
    lines: list[str] = strip_comments(sheet).splitlines()
    i: int = 0
    try:
        while i < len(lines):
            l = lines[i]
            if not l.strip():       i+=1; continue
            if starts_blank(l):
                raise ParseError(i-1, "Unexpected indent")
            entry_type, *l = l.split(maxsplit=1)

            ls = [] if len(l) == 0 else [l[0]]; j=i+1
            default_ls_offset = -len(ls)
            while j < len(lines) and starts_blank(lines[j]):
                ls.append(lines[j].lstrip()); j+=1
            # Join continuation lines
            cl = 0
            while cl < len(ls):
                if len(ls[cl]) > 0 and ls[cl][-1] == '\\':
                    if cl+1 >= len(ls):
                        i+=cl; raise ParseError(i-1, 'Unexpected end of block')
                    ls[cl] = ls[cl][:-1] + ls[cl+1].lstrip()
                    del ls[cl+1]
                else: cl+=1
            if entry_type == "default":
                parse_default(i+default_ls_offset, ls, res)
            elif entry_type == "task":
                parse_task(i, ls, res)
            elif re.match(r'^[0-9]', entry_type):
                if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', entry_type):
                    raise ParseError(i-1, f"Cannot parse date '{entry_type}'")
                parse_day(i, date=entry_type, lines=ls, sheet=res,
                          implicit_tasks=implicit_tasks)
            else:
                raise ParseError(i-1, f"Unknown entry type '{entry_type}'")
            i=j; continue
        return res
    except ParseError as e:
        lno = e.line+1
        lines = sheet.splitlines()
        pre = lines[max(0,lno-2):lno]
        if pre: pre = list(map(lambda x: f'  | {x}', pre))
        post = lines[min(len(lines),lno+1):min(len(lines),lno+4)]
        if post: post = list(map(lambda x: f'  | {x}', post))
        context = (('\n'.join(pre)+'\n') if pre else "") + \
                  f'  > {lines[lno]}\n' + \
                  (('\n'.join(post)+'\n') if post else "")
        raise ParseError(lno, e.msg, context=context) from e
