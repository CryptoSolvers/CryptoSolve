"""
Introduces the CallableRegistry which allows
users to register callables anywhere in the codebase
with a simple decorator or method.
"""
from inspect import signature
from typing import Callable, Dict, Optional
import logging

__all__ = ['CallableRegistry']

def _num_arguments(func: Callable) -> int:
    """Returns the number of arguments of the given function."""
    sig = signature(func)
    return len(sig.parameters)

class CallableRegistry:
    """
    A registry of callables, referenced by
    a name string. Optionally with arity enforced.

    Parameters
    ==========
    enforce_arity: int
      If zero or positive, it will enforce the arity of functions
      registered to match the argument.
    """
    def __init__(self, enforce_arity: int = -1):
        if enforce_arity < 0:
            raise ValueError(f"enforce_arity must be zero or positive not {enforce_arity}.")
        self.enforce_arity = enforce_arity
        self.callables: Dict[str, Callable] = dict()

    def register(self, name: str, func: Optional[Callable] = None) -> Optional[Callable]:
        """
        Decorator or method to register a callable as a given name.

        Parameters
        ==========
        name: str
          The name to register the callable by.
        func: Optional[Callable]
          Its existence determines whether it's registered via the
          decorator or method syntax.

        Examples
        ========
        >>> cr = CallableRegistry()
        >>> @cr.register('test')
        >>> def test_func():
        >>>     print("Test")
        >>> cr.register('test2', lambda: print("Test2"))
        """
        if name in self.callables.keys():
            logging.warning("Overriding callable of name '%s'.", name)
        def assign(func):
            if not callable(func):
                raise ValueError("Argument func must be callable.")
            if self.enforce_arity >= 0 and _num_arguments(func) != self.enforce_arity:
                raise ValueError(
                    f"Function has arity {_num_arguments(func)} not {self.enforce_arity}."
                )
            self.callables[name] = func
            return func

        if func is None:
            return assign
        assign(func)
        return None

    def find(self, name: str) -> Optional[Callable]:
        """
        Find a callable given its name.

        Parameters
        ==========
        name: str
          Name in which the callable was registered under.
        """
        return self.callables.get(name)
