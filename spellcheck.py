import io
import dis
import contextlib
import builtins
from fuzzywuzzy import process
import ipdb

old = builtins.__build_class__

# TODO: recursive application to code objects
# TODO: check if closures work
CodeType = type((lambda: 0).__code__)


def new(body, name, *args, **kwargs):
    bases = args
    print(globals().keys())
    functions = {
        val: spellcheck(val)
        for val in body.__code__.co_consts
        if isinstance(val, CodeType)
    }
    body.__code__ = new_code_from_old(
        body.__code__,
        co_consts=tuple(
            functions.get(const, const) for const in body.__code__.co_consts
        ),
    )
    ret = old(body, name, *bases, **kwargs)
    return ret


builtins.__build_class__ = new


def new_code_from_old(code, **kwargs):
    return CodeType(
        kwargs.get("co_argcount", code.co_argcount),
        kwargs.get("co_kwonlyargcount", code.co_kwonlyargcount),
        kwargs.get("co_nlocals", code.co_nlocals),
        kwargs.get("co_stacksize", code.co_stacksize),
        kwargs.get("co_flags", code.co_flags),
        kwargs.get("co_code", code.co_code),
        kwargs.get("co_consts", code.co_consts),
        kwargs.get("co_names", code.co_names),
        kwargs.get("co_varnames", code.co_varnames),
        kwargs.get("co_filename", code.co_filename),
        kwargs.get("co_name", code.co_name),
        kwargs.get("co_firstlineno", code.co_firstlineno),
        kwargs.get("co_lnotab", code.co_lnotab),
        kwargs.get("co_freevars", code.co_freevars),
        kwargs.get("co_cellvars", code.co_cellvars),
    )


def spellcheck(code):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        dis.dis(code)
    names = []
    for line in f.getvalue().split("\n"):
        if "LOAD_GLOBAL" in line:
            pre, LG, post = line.partition("LOAD_GLOBAL")
            pre, par, post = post.partition("(")
            names.append(post.rstrip(")"))
    available_names = set(globals()) | set(code.co_varnames)
    misspelled = set(names) - available_names
    fixed, badglobals = {}, {}
    for wrong in misspelled:
        better, _ = process.extractOne(wrong, available_names)
        fixed[wrong] = better
        if better not in globals():
            badglobals[code.co_names.index(wrong)] = code.co_varnames.index(better)
    if fixed:
        names = tuple(fixed.get(name, name) for name in code.co_names)
        bytecode = code.co_code
        for bad, good in badglobals.items():
            bytecode = code.co_code.replace(
                ("t" + chr(bad)).encode(), ("|" + chr(good)).encode()
            )
        code = new_code_from_old(code, co_names=names, co_code=bytecode)
    return code


import random


class Employee:
    def __init__(self, name, title):
        self.name = name
        self.title = tilte
        self.salary = radnom.randint(1, 10000)

    def __str__(self):
        return f"<Employee: {self.name}, {self.title} (€{self.salary})>"


e = Employee("Jonathan", "Software developer")
print(e)
