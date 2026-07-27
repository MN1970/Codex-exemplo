"""
Example Python code with various code smells
Used for testing detection rules
"""

import os  # PY001: Unused import
import sys
from collections import *  # PY013: Wildcard import
import json as j

# PY007: Global variable
GLOBAL_STATE = []

# PY014: Reassigned builtin
list = []


def long_function_with_many_lines():  # PY002: Long method (>50 lines)
    """This docstring exists"""
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    return x + y + z


def deeply_nested_function(a, b, c):  # PY012: Too many arguments
    """Missing docstring in complex function"""
    if a:  # PY003: Deep nesting (>3 levels)
        if b:
            if c:
                if a > b:
                    if b > c:
                        pass
    pass  # PY015: Redundant pass


def process_data(items=[]):  # PY008: Mutable default argument
    """Process list items"""
    items.append("new_item")
    return items


def check_value(x):
    """Check if value is None"""
    if x == None:  # PY009: Comparison to None
        return False
    if x != None:  # PY009: Comparison to None
        return True
    return None


def complex_condition(a, b, c, d):  # PY004: Complex condition
    """Function with complex boolean logic"""
    if a > 0 and b < 10 and c == 5 and d != 0:
        return True
    return False


def bare_except_function():  # PY006: Bare except
    """Try/except with bare except"""
    try:
        result = 1 / 0
    except:
        print("Error!")


def use_global_var():  # PY007: Global variable
    """Use global variable"""
    global GLOBAL_STATE
    GLOBAL_STATE.append(1)


def unused_var_function():  # PY010: Unused variable
    """Function with unused variable"""
    unused_value = 42
    important_value = 100
    return important_value


def multiple_statements():  # PY011: Multiple statements per line
    x = 1; y = 2; z = 3  # Multiple statements
    return x + y + z


# PY005: Missing docstring - this function has none
def no_docstring_function():
    return "value"


# PY005: Missing docstring
class NoDocstringClass:
    pass


# PY005: Docstring exists for class
class GoodClass:
    """This class has a docstring"""

    # PY005: Missing docstring
    def no_docstring_method(self):
        pass
