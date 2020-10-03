__all__ = ['PathLike', 'Recursive', 'JSON']

from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple, TypeVar, Union

PathLike = Union[Path, bytes, str]

T = TypeVar('T')

# mypy cannot resolve recursive types
Recursive = Union[T, Tuple['Recursive', ...], List['Recursive'], Dict[Any, 'Recursive']]  # type: ignore
"""
.. note::
    The following values are all "instances" of `Recursive[int]`:

    .. testcode::

        0
        (0, 1)
        [0, 1, 2]
        {'a': 0, 1: 2}
        [[[0], (1, 2, (3,)), {'a': {'b': [4]}}]]

        from collections import namedtuple
        Point = namedtuple('Point', ['x', 'y'])
        Point(0, 1)  # also `Recursive[int]`
"""

JSON = Union[None, bool, int, float, str, List['JSON'], Mapping[str, 'JSON']]  # type: ignore
"""
.. note::
    The following values are all "instances" of `JSON`:

    .. testcode::

        True
        0
        1.0
        'abc'
        [0, 1.0]
        {'a': [0, 1.0], 'b': False, 'c': 'abc'}
"""
