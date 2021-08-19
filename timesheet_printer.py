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
    for d in log.days:
        daily_total = Decimal(0)
        lines.append(d.date)
        for task, time in d.times.items():
            daily_total += time; grand_total += time
            desc = f'{task.name} {task.get("desc")}'
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

def print_hours_only(log: Log) -> str:
    lines = list()
    total_hours = Decimal(0)
    total_net = Decimal(0)
    total_gross = Decimal(0)
    lines.append("Date,Description,Rate,Hours,Net,VAT,Gross")
    for d in log.days:
        for task, time in d.times.items():
            desc = task.get("desc") if ',' not in task.get("desc") \
                   else f'"{task.get("desc")}"'
            rate = task.get("rate") if task.get("rate") != None else \
                   log.get_default("rate") if log.get_default("rate") != None \
                   else ""
            if rate: rate = Decimal(rate)
            net = time*rate if rate else ""
            total_hours += time
            vat = task.get("vat") if task.get("vat") != None else \
                  log.get_default("vat") if log.get_default("vat") != None \
                  else ""
            if vat: vat = Decimal(vat)
            if net: total_net += net
            gross = ""
            if net and vat: gross = net + net * vat
            if gross: total_gross += gross
            lines.append(f'{d.date},{desc},{rate},{time},{net},{vat},'\
                  f'{gross:>.2f}')
    total_net = total_net if total_net else ""
    total_gross = total_gross if total_gross else ""
    lines.append(f'Total,,,{total_hours},{total_net},,{total_gross:>.2f}')
    return '\n'.join(lines)

def print_hours_only_novat(log: Log) -> str:
    lines = list()
    total_hours = Decimal(0)
    total_price = Decimal(0)
    lines.append("Date,Description,Rate,Hours,Price")
    for d in log.days:
        for task, time in d.times.items():
            desc = task.get("desc") if ',' not in task.get("desc") \
                   else f'"{task.get("desc")}"'
            rate = task.get("rate") if task.get("rate") != None else \
                   log.get_default("rate") if log.get_default("rate") != None \
                   else ""
            if rate: rate = Decimal(rate)
            price = time*rate if rate else ""
            total_hours += time
            if price: total_price += price
            lines.append(f'{d.date},{desc},{rate},{time},{price}')
    total_price = total_price if total_price else ""
    lines.append(f'Total,,,{total_hours},{total_price}')
    return '\n'.join(lines)

def print_custom(log: Log, format: str, undefined: str="undefined") -> str:
    lines = list()
    fields = re.findall(r'{([^}:]*)[}:]', format)
    for d in log.days:
        for task, time in d.times.items():
            linedict = dict()
            for f in fields:
                if f == "date":         linedict["date"] = d.date
                elif f == "task":       linedict["task"] = task.name
                elif f == "time":       linedict["time"] = time
                else:                   linedict[f] = task.attrs.get(f, None)
            for k, v in linedict.items():
                if v == None: linedict[k] = undefined
            lines.append(format.format(**linedict))
    return '\n'.join(lines)
