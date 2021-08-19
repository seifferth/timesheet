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
        if desc != None:        t.set_desc(desc)
        elif self.desc != None: t.set_desc(self.desc)
        if rate != None:        t.set_rate(rate)
        elif self.rate != None: t.set_rate(self.rate)
        if vat  != None:        t.set_vat(vat)
        elif self.vat  != None: t.set_vat(self.vat)
        return t
    def __init__(self, name: str):
        self.name: str = name
        self.desc: str = None
        self.rate: Decimal = None
        self.vat:  Decimal = None
    def set_desc(self, desc: str):
        if self.desc != None and desc != self.desc:
            raise ParseError(0,
                f"Cannot set task desc to '{desc}', because it has "\
                f"already been set to '{self.desc}' earlier"
            )
        self.desc = desc
    def set_rate(self, rate: Decimal):
        if self.rate != None and rate != self.rate:
            raise ParseError(0,
                f"Cannot set task rate to '{rate}', because it has "\
                f"already been set to '{self.rate}' earlier"
            )
        self.rate = rate
    def set_vat(self, vat: Decimal):
        if self.vat != None and vat != self.vat:
            raise ParseError(0,
                f"Cannot set task vat to '{vat}', because it has "\
                f"already been set to '{self.vat}' earlier"
            )
        self.vat = vat
    def __hash__(self):
        return hash((self.name, self.rate, self.vat))
    def __repr__(self):
        return f'<Task {self.name}, Rate {self.rate}, VAT {self.vat}, '\
               f'Desc {self.desc}>'
    def __str__(self):
        return self.desc

class Time:
    def __init__(self, time: str):
        try:
            h, m = time.split(":", 1)
            self.__value = Decimal(h)*60 + Decimal(m)
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
        self.tasks: dict[str,Task] = dict()
        self.default_rate: Decimal = None
        self.default_vat: Decimal = None
        self.days: list[Day] = list()
    def set_default_rate(self, rate: Decimal):
        if self.default_rate != None and rate != self.default_rate:
            raise ParseError(0,
                f"Cannot set default rate to '{rate}', because it has "\
                f"already been set to '{self.default_rate}' earlier"
            )
        self.default_rate = rate
    def set_default_vat(self, vat: Decimal):
        if self.default_vat != None and vat != self.default_vat:
            raise ParseError(0,
                f"Cannot set default vat to '{vat}', because it has "\
                f"already been set to '{self.default_vat}' earlier"
            )
        self.default_vat = vat
    def add_task(self, task: Task):
        if task.name in self.tasks.keys():
            raise ParseError(0, f"Task '{task.name}' was already defined")
        self.tasks[task.name] = task
    def get_task(self, name: str):
        if name not in self.tasks.keys():
            raise ParseError(0, f"Task '{name}' referenced before asignment")
        return self.tasks.get(name)
    def add_day(self, day: Day):
        self.days.append(day)