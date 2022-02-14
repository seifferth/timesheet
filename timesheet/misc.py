#!/usr/bin/env python3

import sys
from textwrap import wrap

def __printwrap(severity: str, msg: str, line_number: int,
                filename: str=None) -> None:
    filepart = f"file '{filename}', " if filename else ''
    s = f'{severity} while parsing {filepart}line {line_number+1}: {msg}'
    print('\n'.join(wrap(s, width=79)), file=sys.stderr)

def parser_warning(filename: str, line_number: int, warning: str) -> None:
    __printwrap('Warning', warning, line_number, filename=filename)

def parser_error(filename: str, line_number: int, error: str,
                 context: str=None) -> None:
    __printwrap('Error', error, line_number, filename=filename)
    if context != None:
        print(context, file=sys.stderr, end="")
