#!/usr/bin/env python3

import sys
from textwrap import wrap

def __printwrap(msg: str) -> None:
    print('\n'.join(wrap(msg)), file=sys.stderr)

def parser_warning(line_number: int, warning: str) -> None:
    __printwrap(f'Warning while parsing line {line_number+1}: {warning}')

def parser_error(line_number: int, error: str, context: str=None) -> None:
    __printwrap(f'Error while parsing line {line_number+1}: {error}')
    if context != None:
        print(context, file=sys.stderr, end="")
