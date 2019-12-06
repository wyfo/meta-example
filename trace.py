from ast import (Call, Constant, Expr, List, Load, Name, NodeTransformer,
                 copy_location, fix_missing_locations, parse)
from functools import wraps
from inspect import getsourcelines
from itertools import takewhile
from typing import Callable

from printer import Printer


class Tracer(NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if all(isinstance(arg, Constant) for arg in node.args):
            return node
        return copy_location(Call(
            func=Name(id="__trace__", ctx=Load()),
            args=[node.func, *node.args],
            keywords=node.keywords
        ), node)

    def visit_Assign(self, node):
        self.generic_visit(node)
        if not all(isinstance(tgt, Name) for tgt in node.targets):
            return node
        names = List(
            elts=[Constant(value=tgt.id) for tgt in node.targets],
            ctx=Load()
        )
        values = List(
            elts=[Name(id=tgt.id, ctx=Load()) for tgt in node.targets],
            ctx=Load()
        )
        return node, Expr(Call(func=Name(id="__assign__", ctx=Load()),
                               args=[names, values], keywords=[]))


def getsource(func: Callable) -> str:
    lines, _ = getsourcelines(func)
    nb_spaces = sum(1 for _ in takewhile(str.isspace, lines[0]))
    return "".join(line[nb_spaces:] for line in lines)


def isbuiltin(obj) -> bool:
    return obj.__module__ == "builtins"


def trace(func: Callable, printer: Printer = None):
    printer = printer or Printer()

    @wraps(func)
    def wrapper(*args, **kwargs):
        def __trace__(func, *args, **kwargs):
            return trace(func, printer.indented)(*args, *kwargs)

        def __assign__(names, values):
            printer.indented.print(f"{', '.join(map(str, names))} = "
                                   f"{', '.join(map(str, values))}")

        args_s = ", ".join((
            *map(str, args),
            *(f"{k}={v}" for k, v in kwargs.items())
        ))
        printer.print(f"{func.__name__}({args_s})")
        if isbuiltin(func):
            return func(*args, **kwargs)
        tree = parse(getsource(func))
        traced = fix_missing_locations(Tracer().visit(tree))
        compiled = compile(traced, "<ast>", "exec")
        loc = {}
        glb = {**func.__globals__,
               "__trace__":  __trace__,
               "__assign__": __assign__}
        if func.__globals__["trace"] is trace:
            glb["trace"] = lambda f: f
        exec(compiled, glb, loc)
        return loc[func.__name__](*args, **kwargs)

    return wrapper


def incr(i: int) -> int:
    return i + 1


@trace
def func(i: int):
    if i < 10:
        new_i = incr(i)
        func(new_i)


def test():
    print()
    func(5)
    pass
