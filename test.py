#!/usr/bin/env python3

import os, sys, re
from subprocess import run
from io import StringIO
from difflib import context_diff

class Test:
    #def __init__(self, name: str, args: str, stdin: str,
    #             code: int, stdout: str, stderr: str):
    def __init__(self):
        self.filename: str = None
        self.name: str     = None
        self.skip: bool    = False
        self.args: str     = None
        self.stdin: str    = None
        self.code: int     = None
        self.stdout: str   = None
        self.stderr: str   = None
    def __str__(self):
        return self.name

class TestFailure:
    def __init__(self, name: str, msg: str):
        self.name: str = name
        self.msg: str = msg
    def __str__(self):
        return self.msg

def run_test(test: Test) -> TestFailure:
    p = run(f'./timesheet.py {test.args}', shell=True, input=test.stdin,
            encoding="UTF-8", capture_output=True)
    errmsg = list()
    if test.code != None and p.returncode != test.code:
        errmsg.append("=== Unexpected returncode ===")
        errmsg.append(f'Expected {t.code} but got {p.returncode}')
    if test.stdout != None and p.stdout != test.stdout:
        errmsg.append("=== Unexpected stdout ===")
        errmsg.append(''.join(context_diff(
            test.stdout.splitlines(keepends=True),
            p.stdout.splitlines(keepends=True),
            "Expected", "Actual"
        )))
    if test.stderr != None and p.stderr != test.stderr:
        errmsg.append("=== Unexpected stderr ===")
        errmsg.append(''.join(context_diff(
            test.stderr.splitlines(keepends=True),
            p.stderr.splitlines(keepends=True),
            "Expected", "Actual"
        )))
    return TestFailure(test.name, '\n'.join(errmsg)) if errmsg else None

def load_tests(directory: str):
    fs = sorted(os.listdir(directory))
    fs = map(lambda x: os.path.join(directory, x), fs)
    fs = filter(lambda x: os.path.isfile(x), fs)
    for filename in fs:
        with open(filename) as f:
            tests = re.split(r'-+-->8--+-',
                re.sub(r'-+--8<--+-', '--->8---', f.read())
            )
        for n, t in enumerate(tests, 1):
            if not t.strip(): continue
            attributes = re.split(r'^[ \t]*>+>>[ \t]*', t, flags=re.M)
            t = Test()
            t.filename = filename
            for att in attributes:
                if not att.strip(): continue
                key, sep, val = re.split(r'(=|>+>>[ \t]*\n)', att, maxsplit=1)
                key = key.strip()
                if sep == "=": val = val.strip()
                # Add attributes to test
                if key == "name":       t.name = val
                elif key == "skip":
                    t.skip = True if val.lower() == "true" else False
                elif key == "comment":  pass
                elif key == "args":     t.args = val
                elif key == "code":     t.code = int(val)
                elif key == "stdin":    t.stdin = val
                elif key == "stdout":   t.stdout = val
                elif key == "stderr":   t.stderr = val
                else: raise Exception(f"Unknown test attribute '{key}'")
            if t.name == None: t.name = f'Test {n}'
            yield t

if __name__ == "__main__":
    selection = sys.argv[1:]
    ok, skip, fail = 0, 0, 0
    for t in load_tests("tests"):
        if selection and t.filename not in selection: continue
        testfilename = t.filename if len(t.filename) < 30 \
                                  else t.filename[:28]+".."
        testname = t.name if len(t.name) < 20 else t.name[:38]+".."
        testname = f'{testfilename+":":<30} {testname:<20}'
        if t.skip:
            skip += 1
            print(f'>>> {testname:<50}   {"SKIP":>19}')
            continue
        res = run_test(t)
        if res == None:
            ok += 1
            print(f'>>> {testname:<50}   {"OK":>19}')
        else:
            fail += 1
            print(f'>>> {testname:<50}   {"FAIL":>19}')
            print(res)
            print()
    print('\n'.join(['',
        f'{" ":>50} {  ok:>10}/{ok+skip+fail:<10}   OK',
        f'{" ":>50} {skip:>10}/{ok+skip+fail:<10} SKIP',
        f'{" ":>50} {fail:>10}/{ok+skip+fail:<10} FAIL',
    ]))
    exit(0 if fail == 0 else 1)
