# Beyond metaclasses

*The power of \_\_build_class__*

====

Metaprogramming: code as data

====

Why?

- Avoid code duplication
- Extend Python itself
- Write pythonic interfaces
- Give your code magical abilities

====

Dante's 9 Levels of Metaprogramming Hell

1. decorators
2. magic methods
3. metaclasses
4. overriding builtins
5. inspect
6. ast/dis
7. eval/compile
8. forbiddenfruit/ctypes
9. patching CPython

====

```
[functionality, magic]
^                                   patching CPython
|
|                  __build_class__
|           metaclasses                       eval
|             import hooks
|                            inspect/dis
|                       ast
|
|                          ctypes
|                 patching builtins
|     Magic methods
|  decorators
|
+----------------------------------------------> [surprise, complexity]
```
====

Some fun examples:

- Hy\[1]; import lisp from python
- Pypes\[2]; `-(O| input() | str.split | "," | (map, int) | sum | print)`
- Honestly lots of large libraries: Django, pytest, ...

  


\[1]: github.com/hylang/hy

\[2]: github.com/L3viathan/pypes

====

## Metaclasses

====

some object ∈ some class ∈ some metaclass

Derive from `type` (the default metaclass)

====

```python
class Foo(metaclass=MetaFoo):
    ...
```

====

```python
Foo = MetaFoo("Foo", (), {})  # ...-ish
```

====

```python
class Bar(Foo):
    ...  # also has MetaFoo as metaclass
```

====

Why?

- Registering classes on class creation (!) time
- Patching class body
- Replacing class with different class?

====

# Class decorators

- Can do _most_ of the things you can do with metaclasses
- Explicit
- IMHO almost always better solution than Metaclasses
- Can not do _everything_ metaclasses can do

====

Excursion: Do metaclasses have to derive from type?

====

No; they don't even have to be classes!

```exec
def not_a_class(name, bases, namespace):
    return lambda: "gotcha"

class Foo(metaclass=not_a_class):
    pass
```

====

What if metaclasses aren't powerful enough?

====

*Warning: You are leaving the reasonable sector.*

====

Metaclasses require the class to declare them

- Not very compatible with 3rd-party code
- What if we want to play around with inheritance?

====

```python
class Species:
    def __init__(self, species):
        self.species = species

    def __str__(self):
        return f"<Species: {self.species}>"

cat = Species("Cat")
```

====

```python
class EgyptianMau(cat):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"<{self.__class__.__name__} ({self.species})>: {self.name}"
```

====

This doesn't work, of course.

You can't inherit from instances.

====

We can't really change that with metaclasses, because:

- Either we would need to specify the metaclass-argument in the derived
  class — not user-friendly.
- Or we need to inherit from a _different_ class that has this metaclass,
  but we want to inherit from `cat`.

====

Who calls the metaclass?

====

Surprisingly: Not C-code.

====

`builtins.__build_class__`

====

Called when `class` statement is executed.

Signature: 〈body, name, *args, **kwargs〉

`*args` usually bases, `**kwargs` usually nothing or only `metaclass=`.

But we can change that!

====

```exec
import builtins
old = builtins.__build_class__
def bc(body, name, *args, **kwargs):
    print("Defining", name)
    if args and isinstance(args[0], str):
        print(args[0])
        args = args[1:]
    return old(body, name, *args, **kwargs)
builtins.__build_class__ = bc
```

====

```python
def new(body, name, *args, **kwargs):
    bases = args
    weird = False
    if any(not isinstance(base, type) for base in bases):
        bases = [type(base) for base in bases]
        weird = True
    ret = old(body, name, *bases, **kwargs)
    if weird:
        for base in args:
            for k, v in base.__dict__.items():
                setattr(ret, k, v)
    return ret
```

====

(spelcheck, translate)
