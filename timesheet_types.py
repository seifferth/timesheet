#!/usr/bin/env python3

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
    def copy(self, desc=None, rate=None, vat=None):
        t = Task(self.name)
        t.attrs = { k: v for k, v in self.attrs.items() }
        if desc != None:        t.attrs["desc"] = desc
        if rate != None:        t.attrs["rate"] = rate
        if vat  != None:        t.attrs["vat"]  = vat
        return t
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
    def get(self, key: str) -> str:
        return self.attrs.get(key)
    def __hash__(self):
        return hash((self.name, str([
            (k,self.attrs.get(k)) for k in sorted(self.attrs.keys())
        ])))
    def __repr__(self):
        return f'<Task {self.name}, Attributes: {str(self.attrs)}>'
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

class Day:
    def __init__(self, date):
        self.date: str = date
        self.times: dict[Task,Decimal] = None
    def add_times(self, times: dict[Task,Decimal]) -> None:
        self.times = times

class Log:
    def __init__(self):
        self.taskdefs: dict[str,Task] = dict()
        self.defaults: dict[str,str] = dict()
        self.days: list[Day] = list()
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
    def add_day(self, day: Day):
        self.days.append(day)
