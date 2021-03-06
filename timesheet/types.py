#!/usr/bin/env python3

import re
from decimal import Decimal
from .misc import parser_warning

class ParseError(Exception):
    def __init__(self, line: int, msg: str, context=None,
                 filename: str=None):
        self.line: int = line
        self.msg: str = msg
        self.context: str = context
        self.filename = filename
    def __str__(self):
        return self.msg

class DescPlaceholder():
    pass

class Task:
    def __init__(self, lno: int, name: str):
        self.lno: int = lno
        self.name: str = name
        self.attrs: dict[str,str] = dict()
    def set(self, key: str, val: str):
        if key in self.attrs.keys() and val != self.attrs[key]:
            raise ParseError(self.lno,
                f"Cannot set task {key} to '{val}', because it has "\
                f"already been set to '{self.attrs[key]}' earlier"
            )
        self.attrs[key] = val

class Time:
    def __init__(self, lno: int, time: str):
        self.lno = lno
        self.string = time
        try:
            h, m = time.split(":", 1)
            self.__value = (Decimal(h)*60 + Decimal(m))
        except Exception as e:
            raise ParseError(self.lno, f"Could not parse time '{time}'")
    def decimal(self):
        """Time in minutes since midnight"""
        return self.__value

class EntryStartPoint:
    def __init__(self, filename: str, lno: int, task: str, date: str,
                 start: Time):
        self.filename: str = filename
        self.lno: int = lno
        self.task: str = task
        self.start: Time = start
        self.attrs: dict[str,str] = dict()
        if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date):
            raise ParseError(self.lno, f"Cannot parse date '{date}'")
        self.date: str = date
        self.year, self.month, self.day = date.split("-")
class Entry:
    def __init__(self, start: EntryStartPoint, stop: Time):
        self.task: str = start.task
        self.start: Time = start.start
        self.attrs: dict[str,str] = start.attrs
        self.date: str = start.date
        self.year, self.month, self.day = start.year, start.month, start.day
        self.stop: Time = stop
        self.minutes: Decimal = self.stop.decimal() - self.start.decimal()
        if self.minutes == 0:
            parser_warning(start.filename, start.lno+1,
                f"The time entry for task {self.task} is zero"
            )
        elif self.minutes < 0:
            parser_warning(start.filename, start.lno+1,
                f"The time entry for task {self.task} is negative: "\
                f"{self.minutes/60:.2f} hours"
            )

class Sheet:
    def __init__(self):
        self.tasks: dict[str,Task] = dict()
        self.defaults: dict[str,str] = dict()
        self._defaults_lnos: dict[str,str] = dict()
        self.entries: list[Entry] = list()
    def set_default(self, key, val, lno):
        if key in self.defaults.keys() and val != self.defaults[key]:
            raise ParseError(lno,
                f"Cannot set default {key} to '{val}', because it has "\
                f"already been set to '{self.defaults[key]}' on line "\
                f"{self._defaults_lnos[key]}"
            )
        self.defaults[key] = val
        self._defaults_lnos[key] = lno+2
    def get_default(self, key: str) -> str:
        return self.defaults.get(key)
    def add_task(self, task: Task):
        if task.name in self.tasks.keys():
            known = self.tasks.get(task.name)
            if task.attrs == known.attrs: return
            withdiff = "with different" if known.attrs else "without"
            raise ParseError(task.lno-1,
                f"Task '{task.name}' was already defined {withdiff} "\
                f"attributes on line {known.lno+1}"
            )
        self.tasks[task.name] = task
    def add_entry(self, entry: Entry) -> None:
        self.entries.append(entry)
