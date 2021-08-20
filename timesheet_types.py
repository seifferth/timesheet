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
    def copy(self, date=None):
        t = Task(self.name)
        if date: t.set_date(date)
        t.attrs = { k: v for k, v in self.attrs.items() }
        return t
    def __init__(self, name: str):
        self.name: str = name
        self.attrs: dict[str,str] = dict()
        self.date: str = None
        self.day: str = None; self.month: str = None; self.year: str = None
    def set(self, key: str, val: str):
        if key in self.attrs.keys() and val != self.attrs[key]:
            raise ParseError(0,
                f"Cannot set task {key} to '{val}', because it has "\
                f"already been set to '{self.attrs[key]}' earlier"
            )
        self.attrs[key] = val
    def set_date(self, date: str) -> None:
        if self.date != None:
            raise ParseError(0,
                f"Cannot set task date to '{date}', because it has "\
                f"already been set to '{self.date}' earlier"
            )
        if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date):
            raise ParseError(0, f"Cannot parse date '{date}'")
        self.date = date
        self.year, self.month, self.day = date.split("-")
    def get(self, key: str) -> str:
        return self.attrs.get(key)
    def __repr__(self):
        attrs = [(k, self.attrs.get(k)) for k in sorted(self.attrs.keys())]
        return f'<Task {self.name} {self.date} {attrs}>'
    def __str__(self):
        return self.get("desc")

class Time:
    def __init__(self, time: str):
        try:
            h, m = time.split(":", 1)
            self.__value = (Decimal(h)*60 + Decimal(m))/60
        except Exception as e:
            raise ParseError(0, f"Could not parse time '{time}'")
    def decimal(self):
        """Time in minutes since midnight"""
        return self.__value

class Log:
    def __init__(self):
        self.taskdefs: dict[str,Task] = dict()
        self.defaults: dict[str,str] = dict()
        self.entries: list[tuple[Task,Decimal]] = list()
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
        if task.name in self.taskdefs.keys():
            raise ParseError(0, f"Task '{task.name}' was already defined")
        self.taskdefs[task.name] = task
    def get_task(self, name: str):
        if name not in self.taskdefs.keys():
            raise ParseError(0, f"Task '{name}' referenced before asignment")
        return self.taskdefs.get(name)
    def add_time(self, task: Task, hours: Decimal) -> None:
        self.entries.append((task, hours))
    def get_times(self, begin: str=None, end: str=None) \
                                    -> list[tuple[Task,Decimal]]:
        result = [(k, v) for k, v in self.entries]
        if begin: result = [(k, v) for k, v in result if k.date >= begin]
        if end: result = [(k, v) for k, v in result if k.date < end]
        return result
    def get_days(self) -> set[str]:
        return { e[0].date for e in self.entries }
    def get_fields(self) -> list[str]:
        tasks = [ x[0] for x in self.get_times() ]
        attrs = [ "date", "time", "task", "year", "month", "day" ]
        for k in self.defaults.keys():
            if k not in attrs: attrs.append(k)
        for t in tasks:
            for k in t.attrs.keys():
                if k not in attrs: attrs.append(k)
        return attrs
    def select(self, fields: list[str], undefined="undefined") -> list[dict]:
        lines: dict[tuple[str,Decimal]] = dict()
        keyfields = sorted([ f for f in fields if f != "time" ])
        for task, time in self.get_times():
            linedict = dict()
            for f in keyfields:
                if f == "task":         linedict["task"]  = task.name
                elif f == "date":       linedict["date"]  = task.date
                elif f == "day":        linedict["day"]   = task.day
                elif f == "month":      linedict["month"] = task.month
                elif f == "year":       linedict["year"]  = task.year
                elif f in task.attrs.keys():
                    linedict[f] = task.attrs.get(f)
                elif f in self.get_task(task.name).attrs.keys():
                    linedict[f] = self.get_task(task.name).attrs.get(f)
                elif f in self.defaults.keys():
                    linedict[f] = self.defaults.get(f)
                else:                   linedict[f] = undefined
            key = str([ (f, linedict[f]) for f in keyfields ])
            if key not in lines.keys(): lines[key] = (linedict, Decimal(0))
            lines[key] = (lines[key][0], lines[key][1] + time)
        result = list()
        for linedict, time in lines.values():
            linedict["time"] = time
            result.append(linedict)
        return result
