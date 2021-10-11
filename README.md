# py_annotation_switch
A hack for writing switch statements in type annotations for Python.

## Why should I use this?
You most definitely should not use this in any real capacity, for any project, ever. It is fun as a proof-of-concept, however.

## How do I use this?
`Switch` is the switch-case implementation, used as a context manager. Annotating the designated `keyword` (defaulting to `case`) defines cases. 

Cases are in the form:
```
[keyword]: (*case identifier[s], (
  *statements to evaluate,
))
```

The return value of the case is the last item in the statements tuple.

Simplest case (ha):
```py
from __future__ import annotations
from annotation_switch import __annotations__, Switch

switch_case = Switch(3)
with switch_case:
  case: (0, 1, 2, (
    print("Zero, One, or Two."),
    3 < 3
  ))
  case: (3, (
    print("Three."),
    3 == 3
  ))

print(switch_case.output)  # True
```

Case with default:
```py
from __future__ import annotations
from annotation_switch import __annotations__, Switch, default
# Importing default is not necessary for the code to work as intended,
# but it's included here to quiet intellisense of common IDEs.

switch_case = Switch(5)
with switch_case:
  case: (0, 1, 2, (
    print("Zero, One, or Two."),
    5 < 3
  ))
  case: (3, (
    print("Three."),
    5 == 3
  ))
  case: ("default", (
    print("What comes after 3?"),
    5 > 3
  ))

print(switch_case.output)  # True
```

Case with error being raised when case is not resolved:
```py
from __future__ import annotations
from annotation_switch import __annotations__, Switch, CONFIG

CONFIG.defaults_to_none = False

switch_case = Switch("pineapple")
with switch_case:
  case: ("apple", (
    print("fruit"),
    "fruit"
  ))
  case: ("pine", (
    print("tree"),
    "tree"
  ))

#  raises SwitchCaseNotValidError("pineapple")
```

*Note: After the switch statement is exited at the resolution of the context manager, the `Switch` object is converted to an `OutputWrapper` holding only an `output` member. This is to encourage the user to not reuse the `Switch` object, which might have unintended effects.*
