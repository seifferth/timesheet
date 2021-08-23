#!/usr/bin/env python3

import re
from decimal import Decimal

class ParseError(Exception):
    def __init__(self, line: int, msg: str, context=None):
        self.line: int = line
        self.msg: str = msg
        self.context: str = context
    def __str__(self):
        return self.msg
class ValidationError(Exception):
    pass

class Task:
    def __init__(self, name: str):
        self.name: str = name
        self.attrs: dict[str,str] = dict()
    def set(self, key: str, val: str):
        if key in self.attrs.keys() and val != self.attrs[key]:
            raise ParseError(0,
                f"Cannot set task {key} to '{val}', because it has "\
                f"already been set to '{self.attrs[key]}' earlier"
            )
        self.attrs[key] = val

class Time:
    def __init__(self, time: str):
        self.string = time
        try:
            h, m = time.split(":", 1)
            self.__value = (Decimal(h)*60 + Decimal(m))/60
        except Exception as e:
            raise ParseError(0, f"Could not parse time '{time}'")
    def decimal(self):
        """Time in minutes since midnight"""
        return self.__value

class EntryStartPoint:
    def __init__(self, task: str, date: str, start: Time):
        self.task: str = task
        self.start: Time = start
        self.attrs: dict[str,str] = dict()
        if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date):
            raise ParseError(0, f"Cannot parse date '{date}'")
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
        self.time: Decimal = self.stop.decimal() - self.start.decimal()

class Sheet:
    def __init__(self):
        self.tasks: dict[str,Task] = dict()
        self.defaults: dict[str,str] = dict()
        self.entries: list[Entry] = list()
    def set_default(self, key, val):
        if key in self.defaults.keys() and val != self.defaults[key]:
            raise ParseError(0,
                f"Cannot set default {key} to '{val}', because it has "\
                f"already been set to '{self.defaults[key]}' earlier"
            )
        self.defaults[key] = val
    def get_default(self, key: str) -> str:
        return self.defaults.get(key)
    def add_task(self, task: Task):
        if task.name in self.tasks.keys():
            raise ParseError(0, f"Task '{task.name}' was already defined")
        self.tasks[task.name] = task
    def add_entry(self, entry: Entry) -> None:
        self.entries.append(entry)
    def get_fields(self) -> list[str]:
        attrs = [ "date", "time", "task", "year", "month", "day",
                  "start", "stop" ]
        for k in self.defaults.keys():
            if k not in attrs: attrs.append(k)
        for t in self.tasks.values():
            for k in t.attrs.keys():
                if k not in attrs: attrs.append(k)
        for e in self.entries:
            for k in e.attrs.keys():
                if k not in attrs: attrs.append(k)
        return attrs
    def select(self, fields: list[str], undefined="undefined") -> list[dict]:
        lines: dict[tuple[str,Decimal]] = dict()
        keyfields = sorted([ f for f in fields if f != "time" ])
        for entry in self.entries:
            linedict = dict()
            task = self.tasks.get(entry.task)
            for f in keyfields:
                if f == "task":      linedict["task"]  = entry.task
                elif f == "date":    linedict["date"]  = entry.date
                elif f == "day":     linedict["day"]   = entry.day
                elif f == "month":   linedict["month"] = entry.month
                elif f == "year":    linedict["year"]  = entry.year
                elif f == "start":   linedict["start"] = entry.start.string
                elif f == "stop":    linedict["stop"]  = entry.stop.string
                elif f in entry.attrs.keys():
                    linedict[f] = entry.attrs.get(f)
                elif f in task.attrs.keys():
                    linedict[f] = task.attrs.get(f)
                elif f in self.defaults.keys():
                    linedict[f] = self.defaults.get(f)
                else:                   linedict[f] = undefined
            key = str([ (f, linedict[f]) for f in keyfields ])
            if key not in lines.keys(): lines[key] = (linedict, Decimal(0))
            lines[key] = (lines[key][0], lines[key][1] + entry.time)
        result = list()
        for linedict, time in lines.values():
            linedict["time"] = time
            result.append(linedict)
        return result
