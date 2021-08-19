#!/usr/bin/env python3

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
            desc = f'{task.name} {task.desc}'
            if len(desc) > 57: desc = desc[:55]+".."
            lines.append(
                f'    {desc[:57]:<57} {time/60:>5.2f}'
            )
        lines.append("    "+dot_total(
            f'Total hours {45*" "} {daily_total/60:>5.2f}'
        )); lines.append('')
    lines.append(
        dot_total(f'Grand total{46*" "}{grand_total/60:>10.2f}')
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
            lines.append(f'{d.date},{desc},{rate},{time/60},{net},{vat},'\
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
            desc = task.desc if ',' not in task.desc else f'"{task.desc}"'
            rate = task.rate if task.rate != None else log.default_rate \
                             if log.default_rate != None else ""
            price = time/60*rate if rate else ""
            total_hours += time/60
            if price: total_price += price
            lines.append(f'{d.date},{desc},{rate},{time/60},{price}')
    total_price = total_price if total_price else ""
    lines.append(f'Total,,,{total_hours},{total_price}')
    return '\n'.join(lines)
