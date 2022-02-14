#!/usr/bin/env python3

import re, csv
from io import StringIO
from .types import *

def select(sheets: list[Sheet], fields: list[str],
           undefined="undefined") -> list[dict]:
    lines: dict[tuple[str,Decimal]] = dict()
    keyfields = sorted([ f for f in fields
                         if f not in ['hours', 'minutes'] ])
    for sheet in sheets:
        for entry in sheet.entries:
            linedict = dict()
            task = sheet.tasks.get(entry.task)
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
                elif f in sheet.defaults.keys():
                    linedict[f] = sheet.defaults.get(f)
                else:                   linedict[f] = undefined
            key = str([ (f, linedict[f]) for f in keyfields ])
            if key not in lines.keys(): lines[key] = (linedict, Decimal(0))
            lines[key] = (lines[key][0], lines[key][1] + entry.minutes)
    result = list()
    for linedict, minutes in lines.values():
        linedict["minutes"] = minutes
        linedict["hours"] = minutes/60
        result.append(linedict)
    return result

def get_fields(sheets: list[Sheet]) -> list[str]:
    attrs = [ "date", "year", "month", "day", "task", DescPlaceholder,
              "hours", "minutes", "start", "stop" ]
    for sheet in sheets:
        for k in sheet.defaults.keys():
            if k not in attrs: attrs.append(k)
        for t in sheet.tasks.values():
            for k in t.attrs.keys():
                if k not in attrs: attrs.append(k)
        for e in sheet.entries:
            for k in e.attrs.keys():
                if k not in attrs: attrs.append(k)
    if "desc" in attrs:
        attrs.remove("desc")
        attrs[attrs.index(DescPlaceholder)] = "desc"
    else:
        attrs.remove(DescPlaceholder)
    return attrs

def dot_total(total: str) -> str:
    return total[:total.find("  ")+1] + \
           len(total[total.find("  ")+1:total.rfind("  ")+1]) * '.' + \
           total[total.rfind("  ")+1:]

def print_sum(sheets: list[Sheet]) -> str:
    lines = list()
    grand_total = Decimal(0)
    daily_rows: dict[str,list] = dict()
    for row in select(sheets, ["date", "task", "desc", "hours"],
                      undefined=""):
        if row["date"] not in daily_rows.keys():
            daily_rows[row["date"]] = list()
        daily_rows[row["date"]].append({ k: v for k, v in row.items()
                                              if k != "date" })
    for date in sorted(daily_rows.keys()):
        daily_total = Decimal(0)
        lines.append(date)
        for row in daily_rows[date]:
            hours = row["hours"]
            daily_total += hours; grand_total += hours
            desc = f'{row["task"]} {row["desc"]}'
            if len(desc) > 57: desc = desc[:55]+".."
            lines.append(
                f'    {desc[:57]:<57} {hours:>5.2f}'
            )
        lines.append("    "+dot_total(
            f'Total hours {45*" "} {daily_total:>5.2f}'
        )); lines.append('')
    lines.append(
        dot_total(f'Grand total{46*" "}{grand_total:>10.2f}')
    )
    return '\n'.join(lines)+'\n'

def print_custom(sheets: list[Sheet], format: str,
                 undefined: str="undefined") -> str:
    lines = list()
    format = format.replace("{hours}", "{hours:.2f}") # Set default format
    fields = set(re.findall(r'{([^}:]*)[}:]', format))
    for linedict in select(sheets, fields, undefined=undefined):
        lines.append(format.format(**linedict))
    return '\n'.join(lines)+'\n'

def print_csv(sheets: list[Sheet], fields: list[str],
              undefined: str="") -> str:
    result = StringIO()
    if '*' in fields:
        available_fields = []
        for s in sheets:
            for f in s.get_fields():
                if f not in available_fields: available_fields.append(f)
        while '*' in fields:
            i = fields.index('*')
            fields[i:i+1] = available_fields
    w = csv.writer(result, lineterminator="\n")
    w.writerow(fields)
    for row in select(sheets, fields, undefined=undefined):
        if "hours" in row.keys(): row["hours"] = f'{row["hours"]:.2f}'
        w.writerow([ row[f] for f in fields ])
    result.seek(0); return result.read()
