from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional

_PREDEFINED_CASE = object()


class Config:
    """Defines how switch cases operate."""
    __slots__ = ["keyword", "defaults_to_none"]

    def __init__(self):
        self.keyword = "case"
        self.defaults_to_none = True


class SwitchCaseNotValidError(Exception):
    pass


CONFIG = Config()

default = "default"


@dataclass(frozen=True)
class OutputWrapper:
    """Holds the output after the resolution of a Switch statement."""
    output: Any


class Switch:
    """A context-manager implementation of a switch-case."""

    def __init__(self, with_value, scope: Optional[dict] = None):
        self.with_value = with_value
        self.output = None
        self.scope = {} if scope is None else scope
        self.scope["default"] = default

    def __enter__(self):
        __annotations__.clear()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Resolves value to a case, runs code associated with case, and forces Switch to be unusable as a Switch
        statement again."""
        self.output = __annotations__.resolve(self.with_value, self.scope)
        __annotations__.clear()
        self.__dict__ = {"output": self.output}
        self.__class__ = OutputWrapper


class _IAnnotations(ABC):
    """When imported, overwrites the current context's `__annotations__` and acts as a means to store cases."""
    def __setitem__(self, key, value):
        """Updates cases in the current context."""
        raise NotImplemented

    def resolve(self, value, scope):
        """Resolves a value to either the its corresponding case, a default case, or None."""
        raise NotImplemented

    def clear(self):
        """Clears the cases in the current context."""
        raise NotImplemented


def __c(w):
    return w()


@__c
class __annotations__(_IAnnotations):
    cases = {}
    default = _PREDEFINED_CASE

    def __setitem__(self, key, value):
        if not key == CONFIG.keyword:
            return

        idx = _get_matching_bracket_position(value[:-1])
        identifier = value[1:idx]
        code = value[idx:-1]

        for elem in eval("{" + identifier + "}"):
            if elem == default:
                self.default = code
            else:
                self.cases[elem] = code

    def clear(self):
        self.cases = {}
        self.default = _PREDEFINED_CASE

    def resolve(self, value: Any, scope: dict):
        try:
            code = self.cases[value]
        except KeyError:
            if self.default == _PREDEFINED_CASE:
                if CONFIG.defaults_to_none:
                    code = "(None,)"
                else:
                    raise SwitchCaseNotValidError(value)
            else:
                code = self.default

        code_result = eval(code, scope)

        return code_result[-1]


def _get_matching_bracket_position(check_string: str):
    """Gets first matching bracket position going from last character. Respects parenthesis in quotes."""
    bracket_tally = 0

    class QuoteState:
        DEFAULT = 0
        DOUBLE_QUOTE = 1
        SINGLE_QUOTE = 2

    quote_state = QuoteState.DEFAULT

    for idx, item in enumerate(reversed(check_string)):
        if quote_state == QuoteState.DEFAULT:
            if item == "(":
                bracket_tally -= 1
            elif item == ")":
                bracket_tally += 1
            elif item == "'":
                quote_state = QuoteState.SINGLE_QUOTE
            elif item == '"':
                quote_state = QuoteState.DOUBLE_QUOTE
        else:
            if item == "'" and quote_state == QuoteState.SINGLE_QUOTE:
                quote_state = QuoteState.DEFAULT
            elif item == '"' and quote_state == QuoteState.DOUBLE_QUOTE:
                quote_state = QuoteState.DEFAULT

        if bracket_tally == 0:
            return len(check_string) - idx - 1

    raise Exception("Cannot find matching bracket for code.")
