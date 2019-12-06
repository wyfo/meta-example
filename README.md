Small project to give an overview of Python metaprogramming capacity, focusing on AST transformation.

It contains a decorator `trace` which allows to print all the execution path descending from the decorated function. The execution path consists of function call with serialized arguments and assignments; for the moment (and maybe for ever as it was only a quick demonstration project), local functions are not handled by the trace.

An example will be more explicit than the previous explaination:
```python
from trace import trace
    
def incr(i: int) -> int:
    return i + 1


@trace
def func(i: int):
    if i < 10:
        new_i = incr(i)
        func(new_i)


func(5) # will print
# func(5)
#	incr(5)
#	new_i = 6
#	func(6)
#		incr(6)
#		new_i = 7
#		func(7)
#			incr(7)
#			new_i = 8
#			func(8)
#				incr(8)
#				new_i = 9
#				func(9)
#					incr(9)
#					new_i = 10
#					func(10)
```
