from __future__ import annotations

from abc import ABC
import ast
from ast import Expression, Constant, Name
from dataclasses import dataclass
from typing import Any, Optional

_PREDEFINED_CASE = object()


class Config:
    """Defines how switch cases operate."""
    __slots__ = ["keyword", "defaults_to_none", "fallthrough"]

    def __init__(self):
        self.keyword = "case"
        self.defaults_to_none = True
        self.fallthrough = False


class SwitchCaseNotValidError(Exception):
    pass


CONFIG = Config()

default = "default"


@dataclass(frozen=True)
class OutputWrapper:
    """Holds the output after the resolution of a Switch statement."""
    output: Any


class Switch:
    """A context-manager implementation of a switch-case.

    Annotations must be in the form:
    [keyword]: (*case_identifiers, (*statements,))

    Notice: "statements" has to be a tuple.
    """

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


def parse_annotation(val):
    a = ast.parse(val, mode="eval")
    if isinstance(a, Expression):
        return a
    else:
        raise Exception(f"Invalid AST: {a}")


class CaseIdentifierNotConstantError(Exception):
    pass


class _Case:
    def __init__(self, value_str: str):
        self.value_str = value_str
        expr = parse_annotation(value_str)
        identifiers = set()
        code = None
        self.is_default_case = False

        for ind, elem in enumerate(expr.body.elts):
            if not isinstance(elem, Constant) and ind != len(expr.body.elts) - 1:
                if isinstance(elem, Name) and elem.id == "default":
                    self.is_default_case = True
                else:
                    raise CaseIdentifierNotConstantError(f"{elem} -> case identifier number: {ind}")
            elif ind != len(expr.body.elts) - 1:
                identifiers.add(elem.value)
            else:
                code = expr

        self.identifiers = identifiers
        self.code = code


def __c(w):
    return w()


@__c
class __annotations__(_IAnnotations):
    cases = {}
    default = _PREDEFINED_CASE

    def __setitem__(self, key, value):
        if not key == CONFIG.keyword:
            return

        case = _Case(value)
        for identifier in case.identifiers:
            self.cases[identifier] = case.code
        if case.is_default_case:
            self.default = case.code

    def clear(self):
        self.cases = {}
        self.default = _PREDEFINED_CASE

    def resolve(self, value: Any, scope: dict):

        def compile_and_eval(c, s):
            return eval(compile(c, filename="<unused>", mode="eval"), s)

        try:
            code_result = compile_and_eval(self.cases[value], scope)
        except KeyError:
            if self.default == _PREDEFINED_CASE:
                if CONFIG.defaults_to_none:
                    code_result = (None,)
                else:
                    raise SwitchCaseNotValidError(value)
            else:
                code_result = compile_and_eval(self.default, scope)

        code_result = code_result[-1]

        if isinstance(code_result, tuple):
            return code_result[-1]
        else:
            return code_result
