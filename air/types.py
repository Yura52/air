__all__ = ['PathLike', 'Recursive', 'JSON', 'Part', 'optionals']

import dataclasses as dc
import enum
import os
import typing as ty
from pathlib import Path

PathLike = ty.Union[Path, str, os.PathLike]

T = ty.TypeVar('T')

# mypy cannot resolve recursive types
Recursive = ty.Union[  # type: ignore
    T,
    ty.Tuple['Recursive', ...],  # type: ignore
    ty.List['Recursive'],  # type: ignore
    ty.Dict[ty.Any, 'Recursive'],  # type: ignore
]
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

JSON = ty.Union[  # type: ignore
    None,
    bool,
    int,
    float,
    str,
    ty.List['JSON'],  # type: ignore
    ty.Mapping[str, 'JSON'],  # type: ignore
]
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


class Part(enum.Enum):
    TRAIN = 'train'
    VAL = 'val'
    TEST = 'test'

    @property
    def is_train(self) -> bool:
        return self == Part.TRAIN

    @property
    def is_val(self) -> bool:
        return self == Part.VAL

    @property
    def is_test(self) -> bool:
        return self == Part.TEST


@ty.no_type_check
def _optionals_impl(cls: type, *args, **kwargs) -> type:
    if dc.is_dataclass(cls):
        assert not args and not kwargs
    else:
        cls = dc.dataclass(*args, **kwargs)(cls)
    fields = []
    for x in dc.fields(cls):
        # https://docs.python.org/3/library/dataclasses.html#dataclasses.Field
        kwargs = {
            k: getattr(x, k)
            for k in [
                'default',
                'default_factory',
                'init',
                'repr',
                'hash',
                'compare',
                'metadata',
            ]
        }
        if isinstance(kwargs['default'], dc._MISSING_TYPE) and isinstance(
            kwargs['default_factory'], dc._MISSING_TYPE
        ):
            kwargs['default'] = None
        type_ = (
            x.type
            if getattr(x.type, '_name', None) == 'Optional'
            else ty.Optional[x.type]
        )
        fields.append((x.name, type_, dc.field(**kwargs)))
    return dc.make_dataclass(
        cls.__name__,
        fields,
        **{
            k: getattr(cls.__dataclass_params__, k)
            for k in dir(cls.__dataclass_params__)
            if not k.startswith('_')
        }
    )


@ty.no_type_check
def optionals(
    cls: ty.Optional[type] = None, *args, **kwargs
) -> ty.Union[type, ty.Callable]:
    """Make a dataclass; make all fields Optionals with None as the default value.

    Examples::

        @optionals
        class A:
            b: int
            c: str = 'abc'
        assert A() == A(None, 'abc')

        @optionals(frozen=True)
        class A:
            b: int
        x = A(1)
        x.b = 2  # raises exception
    """

    def f(cls_: type) -> type:
        return _optionals_impl(cls_, *args, **kwargs)

    # check if the decorator is used with paranthesis
    return f(cls) if cls else f
