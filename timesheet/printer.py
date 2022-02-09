#!/usr/bin/env python3

import re, csv
from io import StringIO
from common_types import *

def dot_total(total: str) -> str:
    return total[:total.find("  ")+1] + \
           len(total[total.find("  ")+1:total.rfind("  ")+1]) * '.' + \
           total[total.rfind("  ")+1:]

def print_sum(sheet: Sheet) -> str:
    lines = list()
    grand_total = Decimal(0)
    daily_rows: dict[str,list] = dict()
    for row in sheet.select(["date", "task", "desc", "hours"], undefined=""):
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

def print_custom(sheet: Sheet, format: str, undefined: str="undefined") -> str:
    lines = list()
    format = format.replace("{hours}", "{hours:.2f}") # Set default hours format
    fields = set(re.findall(r'{([^}:]*)[}:]', format))
    for linedict in sheet.select(fields):
        lines.append(format.format(**linedict))
    return '\n'.join(lines)+'\n'

def print_csv(sheet: Sheet, fields: list[str]) -> str:
    result = StringIO()
    w = csv.writer(result, lineterminator="\n")
    w.writerow(fields)
    for row in sheet.select(fields, undefined=""):
        if "hours" in row.keys(): row["hours"] = f'{row["hours"]:.2f}'
        w.writerow([ row[f] for f in fields ])
    result.seek(0); return result.read()
