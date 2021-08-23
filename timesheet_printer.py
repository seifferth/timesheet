#!/usr/bin/env python3

import re, csv
from io import StringIO
from timesheet_types import *

def dot_total(total: str) -> str:
    return total[:total.find("  ")+1] + \
           len(total[total.find("  ")+1:total.rfind("  ")+1]) * '.' + \
           total[total.rfind("  ")+1:]

def print_sum(log: Log) -> str:
    lines = list()
    grand_total = Decimal(0)
    daily_rows: dict[str,list] = dict()
    for row in log.select(["date", "task", "desc", "time"], undefined=""):
        if row["date"] not in daily_rows.keys():
            daily_rows[row["date"]] = list()
        daily_rows[row["date"]].append({ k: v for k, v in row.items()
                                              if k != "date" })
    for date in sorted(daily_rows.keys()):
        daily_total = Decimal(0)
        lines.append(date)
        for row in daily_rows[date]:
            time = row["time"]
            daily_total += time; grand_total += time
            desc = f'{row["task"]} {row["desc"]}'
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
    return '\n'.join(lines)+'\n'

def print_custom(log: Log, format: str, undefined: str="undefined") -> str:
    lines = list()
    format = format.replace("{time}", "{time:.2f}") # Set default time format
    fields = set(re.findall(r'{([^}:]*)[}:]', format))
    for linedict in log.select(fields):
        lines.append(format.format(**linedict))
    return '\n'.join(lines)+'\n'

def print_hours_only(log: Log) -> str:
    result = StringIO()
    total_time, total_net, total_gross = Decimal(0), Decimal(0), Decimal(0)
    w = csv.writer(result, lineterminator="\n")
    w.writerow(["Date","Description","Rate","Hours","Net","VAT","Gross"])
    for row in log.select(["date","desc","rate","time","vat"], undefined=""):
        rate = Decimal(row["rate"])
        vat = Decimal(row["vat"])
        net = row["time"] * rate
        gross = net + net * vat
        total_time += row["time"]; total_net += net; total_gross += gross
        w.writerow([row["date"],row["desc"],row["rate"],f'{row["time"]:.2f}',
                    f'{net:.2f}',row["vat"],f'{gross:.2f}'])
    w.writerow(["Total","","",f'{total_time:.2f}',f'{total_net:.2f}',"",
                f'{total_gross:.2f}'])
    result.seek(0); return result.read()

def print_hours_only_novat(log: Log) -> str:
    result = StringIO()
    total_time, total_net = Decimal(0), Decimal(0)
    w = csv.writer(result, lineterminator="\n")
    w.writerow(["Date","Description","Rate","Hours","Price"])
    for row in log.select(["date","desc","rate","time"], undefined=""):
        rate = Decimal(row["rate"])
        net = row["time"] * rate
        total_time += row["time"]; total_net += net
        w.writerow([row["date"],row["desc"],row["rate"],f'{row["time"]:.2f}',
                    f'{net:.2f}'])
    w.writerow(["Total","","",f'{total_time:.2f}',f'{total_net:.2f}'])
    result.seek(0); return result.read()

def print_csv(log: Log, fields: list[str]) -> str:
    result = StringIO()
    w = csv.writer(result, lineterminator="\n")
    w.writerow(fields)
    for row in log.select(fields, undefined=""):
        if "time" in row.keys(): row["time"] = f'{row["time"]:.2f}'
        w.writerow([ row[f] for f in fields ])
    result.seek(0); return result.read()
