#!/usr/bin/env python3

import re
from timesheet_types import *

def dot_total(total: str) -> str:
    return total[:total.find("  ")+1] + \
           len(total[total.find("  ")+1:total.rfind("  ")+1]) * '.' + \
           total[total.rfind("  ")+1:]

def print_sum(log: Log) -> str:
    lines = list()
    grand_total = Decimal(0)
    for date in log.get_days():
        daily_total = Decimal(0)
        lines.append(date)
        entries: dict[str,Decimal] = dict()
        for task, time in log.get_times(begin=date, end=date+"a"):
            daily_total += time; grand_total += time
            desc = f'{task.name} {task.get("desc")}'
            if desc not in entries: entries[desc] = Decimal(0)
            entries[desc] += time
        for desc, time in entries.items():
            if len(desc) > 57: desc = desc[:55]+".."
            lines.append(
                f'    {desc[:57]:<57} {time:>5.2f}'
            )
        lines.append("    "+dot_total(
            f'Total hours {45*" "} {daily_total:>5.2f}'
        )); lines.append('')
    lines.append(
        dot_total(f'Grand total{46*" "}{grand_total:>10.2f}')
    )
    return '\n'.join(lines)

def print_custom(log: Log, format: str, undefined: str="undefined") -> str:
    lines = list()
    format = format.replace("{time}", "{time:.2f}") # Set default time format
    fields = set(re.findall(r'{([^}:]*)[}:]', format))
    entries: dict[str,list] = dict()
    for task, time in log.get_times():
        linedict = dict()
        linedict["time"] = Decimal(0)
        for f in fields:
            if f == "date":         linedict["date"] = task.date
            elif f == "task":       linedict["task"] = task.name
            elif f == "time":       pass
            elif f in task.attrs.keys():
                linedict[f] = task.attrs.get(f)
            elif f in log.get_task(task.name).attrs.keys():
                linedict[f] = log.get_task(task.name).attrs.get(f)
            elif f in log.defaults.keys():
                linedict[f] = log.defaults.get(f)
            else:                   linedict[f] = undefined
        line_as_key = format.format(**linedict)
        if line_as_key not in entries.keys():
            entries[line_as_key] = [linedict, Decimal(0)]
        entries[line_as_key][1] += time
    for linedict, time in entries.values():
        linedict["time"] = time
        lines.append(format.format(**linedict))
    return '\n'.join(lines)

def print_hours_only(log: Log) -> str:
    return "Date,Description,Rate,Hours,Net,VAT,Gross\n" + \
        print_custom(log, '{date},"{desc}",{rate},{time},,{vat},',
                     undefined="") + \
        "\nTotal,,,,,,"

def print_hours_only_novat(log: Log) -> str:
    return "Date,Description,Rate,Hours,Price\n" + \
        print_custom(log, '{date},"{desc}",{rate},{time},', undefined="") + \
        "\nTotal,,,,"
