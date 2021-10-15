# py_annotation_switch
A hack for writing switch statements in type annotations for Python.

## Why should I use this?
You most definitely should not use this in any real capacity, for any project, ever. It is fun as a proof-of-concept, however. *This is done solely for entertainment purposes.*
 
## How do I use this?
`Switch` is the switch-case implementation, used as a context manager. Annotating the designated `keyword` (defaulting to `case`) defines cases. 

Cases are in the form:
```
[keyword]: (*case identifier[s], (
  *statements to evaluate,
))
```

If `statements` is a tuple, the output value of the switch statement is what the last element evaluates to. If `statements` is any other type, it itself is evaluated as the output value.

Simplest case (ha):
```py
from __future__ import annotations
from annotation_switch import __annotations__, Switch

switch_case = Switch(3)
with switch_case:
  case: (0, 1, 2, (
    print("Zero, One, or Two."),
    3 < 3  # False
  ))
  case: (3, (
    print("Three."),
    3 == 3  # True
  ))

print(switch_case.output)  # True
```

Case with default:
```py
from __future__ import annotations
from annotation_switch import *

switch_case = Switch(5)
with switch_case:
  case: (0, 1, 2, (
    print("Zero, One, or Two."),
    5 < 3  # False
  ))
  case: (3, (
    print("Three."),
    5 == 3  # False
  ))
  case: ("default", (
    print("What comes after 3?"),
    5 > 3  # True
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

*Also note: `__annotations__` is a required import for the package to function. You can equivalently use the import `from annotation_switch import *` which will perform the import automatically.*
