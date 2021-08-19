#!/usr/bin/env python3

import re, sys
from decimal import Decimal

class ParseError(Exception):
    pass
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
            raise ParseError(
                f"Cannot set task desc to '{desc}', because it has "\
                f"already been set to '{self.desc}' earlier"
            )
        self.desc = desc
    def set_rate(self, rate: Decimal):
        if self.rate != None and rate != self.rate:
            raise ParseError(
                f"Cannot set task rate to '{rate}', because it has "\
                f"already been set to '{self.rate}' earlier"
            )
        self.rate = rate
    def set_vat(self, vat: Decimal):
        if self.vat != None and vat != self.vat:
            raise ParseError(
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
            raise ParseError(f"Could not parse time '{time}'")
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
            raise ParseError(
                f"Cannot set default rate to '{rate}', because it has "\
                f"already been set to '{self.default_rate}' earlier"
            )
        self.default_rate = rate
    def set_default_vat(self, vat: Decimal):
        if self.default_vat != None and vat != self.default_vat:
            raise ParseError(
                f"Cannot set default vat to '{vat}', because it has "\
                f"already been set to '{self.default_vat}' earlier"
            )
        self.default_vat = vat
    def add_task(self, task: Task):
        if task.name in self.tasks.keys():
            raise ParseError(f"Task '{task.name}' was already defined")
        self.tasks[task.name] = task
    def get_task(self, name: str):
        if name not in self.tasks.keys():
            raise ParseError(f"Task '{name}' referenced before asignment")
        return self.tasks.get(name)
    def add_day(self, day: Day):
        self.days.append(day)

def parse_day(date: str, lines: list[str], log: Log) -> None:
    d = Day(date)
    times: dict[Task,Decimal] = dict()
    global_start: Time = None
    last_start: Time = None
    for l in lines:
        if re.match(r'^[^0-9\s]', l):       # Attribute line
            raise ParseErrror('Continuation lines for time level overrides '\
                              'are not implemented yet')
        elif re.match(r'^[0-9]', l):        # Time entry
            try:
                time, entry_type, *l = l.split(maxsplit=2)
            except:
                raise ParseError('Unable to parse time entry')
            time = Time(time)
            l = None if len(l) == 0 else l[0]
            if entry_type == "stop":
                if global_start == None: raise ParseError(
                    "Cannot stop time entry without starting it first"
                )
                # TODO: Use global start for double-checking
                times[task] += time.decimal() - last_start.decimal()
                global_start = None
                last_start = None
            elif entry_type == "start" and l == None:
                if not global_start == None: raise ParseError(
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
                task = log.get_task(task)
                if l:       # TODO: Add support for multiple overrides
                    key, val = re.split(r'\s*=\s', l, maxsplit=1)
                    if key == "desc":           task = task.copy(desc=val)
                    elif key == "rate":         task = task.copy(rate=val)
                    elif key == "vat":          task = task.copy(vat=val)
                    else: raise ParseError(
                        f"Time entry level overrides of '{key}' are "\
                        f"been implemented yet"
                    )
                if task not in times.keys(): times[task] = Decimal(0)
                last_start = time
            else:
                raise ParseError(f"Unknown time entry type '{entry_type}'")
    d.add_times(times)
    log.add_day(d)

def parse_task(lines: list[str], log: Log) -> None:
    name, l = lines[0].split(maxsplit=1)
    t = Task(name)
    for l in [l, *lines[1:]]:
        key, val = re.split(r'\s*=\s', l, maxsplit=1)
        if key == "desc":       t.set_desc(val)
        elif key == "rate":     t.set_rate(Decimal(val))
        elif key == "vat":      t.set_vat(Decimal(val))
        else: raise ParseError(f"Unknown task attribute '{key}'")
    log.add_task(t)

def parse_default(lines: list[str], log: Log) -> None:
    for l in lines:
        key, val = re.split(r'\s*=\s', l, maxsplit=1)
        if key == "rate":  log.set_default_rate(Decimal(val))
        elif key == "vat": log.set_default_vat(Decimal(val))
        else: raise ParseError(f"Unknown default value '{key}'")

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
                raise ParseError("Unexpected indent")
            entry_type, *l = l.split(maxsplit=1)

            ls = [] if len(l) == 0 else [l[0]]; j=i+1
            while j < len(lines) and starts_blank(lines[j]):
                ls.append(lines[j].lstrip()); j+=1
            # Join continuation lines
            cl = 0
            while cl < len(ls):
                if len(ls[cl]) > 0 and ls[cl][-1] == '\\':
                    if cl+1 >= len(ls):
                        i+=cl; raise ParseError('Unexpected end of block')
                    ls[cl] = ls[cl][:-1] + ls[cl+1].lstrip()
                    del ls[cl+1]
                else: cl+=1
            if entry_type == "default":
                parse_default(ls, res)
            elif entry_type == "task":
                parse_task(ls, res)
            elif re.match(r'^[0-9]', entry_type):
                if not re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', entry_type):
                    raise ParseError(f"Cannot parse date '{entry_type}'")
                parse_day(date=entry_type, lines=ls, log=res)
            else:
                raise ParseError(f"Unknown entry type '{entry_type}'")
            i=j; continue
        return res
    except ParseError as e:
        print(f'Error while parsing line {i+1}:', e, file=sys.stderr)
        pre = lines[max(0,i-2):i]
        if pre: pre = list(map(lambda x: f'  | {x}', pre))
        post = lines[min(len(lines),i+1):min(len(lines),i+4)]
        if post: post = list(map(lambda x: f'  | {x}', post))
        context = (('\n'.join(pre)+'\n') if pre else "") + \
                  f'  > {lines[i]}\n' + \
                  (('\n'.join(post)+'\n') if post else "")
        print(context, file=sys.stderr, end="")
        exit(1)

def dot_total(total: str) -> str:
    return total[:total.find("  ")+1] + \
           len(total[total.find("  ")+1:total.rfind("  ")+1]) * '.' + \
           total[total.rfind("  ")+1:]

if __name__ == "__main__":
    log: Log = parse(sys.stdin.read())
    if sys.argv[1] == "sum":
        grand_total = Decimal(0)
        for d in log.days:
            daily_total = Decimal(0)
            print(d.date)
            for task, time in d.times.items():
                daily_total += time; grand_total += time
                desc = f'{task.name} {task.desc}'
                if len(desc) > 57: desc = desc[:55]+".."
                print(
                    f'    {desc[:57]:<57} {time/60:>5.2f}'
                )
            print("    "+dot_total(
                f'Total hours {45*" "} {daily_total/60:>5.2f}'
            ), end='\n\n')
        print(
            dot_total(f'Grand total{46*" "}{grand_total/60:>10.2f}')
        )
    if sys.argv[1] == "hours_only":
        total_hours = Decimal(0)
        total_net = Decimal(0)
        total_gross = Decimal(0)
        print("Date,Description,Rate,Hours,Net,VAT,Gross")
        for d in log.days:
            for task, time in d.times.items():
                desc = task.desc if ',' not in task.desc else f'"{task.desc}"'
                rate = task.rate if task.rate != None else log.default_rate \
                                 if log.default_rate != None else ""
                net = time/60*rate if rate else ""
                total_hours += time/60
                vat = task.vat if task.vat != None else log.default_vat \
                               if log.default_vat != None else ""
                if net: total_net += net
                gross = ""
                if net and vat: gross = net + net * vat
                if gross: total_gross += gross
                print(f'{d.date},{desc},{rate},{time/60},{net},{vat},'\
                      f'{gross:>.2f}')
        total_net = total_net if total_net else ""
        total_gross = total_gross if total_gross else ""
        print(f'Total,,,{total_hours},{total_net},,{total_gross:>.2f}')
    if sys.argv[1] == "hours_only_novat":
        total_hours = Decimal(0)
        total_price = Decimal(0)
        print("Date,Description,Rate,Hours,Price")
        for d in log.days:
            for task, time in d.times.items():
                desc = task.desc if ',' not in task.desc else f'"{task.desc}"'
                rate = task.rate if task.rate != None else log.default_rate \
                                 if log.default_rate != None else ""
                price = time/60*rate if rate else ""
                total_hours += time/60
                if price: total_price += price
                print(f'{d.date},{desc},{rate},{time/60},{price}')
        total_price = total_price if total_price else ""
        print(f'Total,,,{total_hours},{total_price}')
