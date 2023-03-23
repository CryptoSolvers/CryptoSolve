"""
Contains various schedules for MOO Programs
"""
from symcollab.algebra.callable_registry import CallableRegistry

__all__ = ['MOO_Schedule', 'every_schedule', 'end_schedule']

MOO_Schedule = CallableRegistry(enforce_arity=1)

@MOO_Schedule.register('every')
def every_schedule(_: int) -> bool:
    """
    Returns the cipher block to the advesary
    at each iteration.
    """
    return True

@MOO_Schedule.register('end')
def end_schedule(_: int) -> bool:
    """Only return the cipher block at the end."""
    return False
