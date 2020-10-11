"""Poor man's experiments management."""

__all__ = ['Experiment']

import enum
import shutil
import sys
import typing as ty
from pathlib import Path

from .io import dump_json, dump_pickle, load_json, load_pickle
from .types import JSON, PathLike


class _Mode(enum.Enum):
    EXIST_OK = 'exist_ok'
    EXIST_NOT_OK = 'exist_not_ok'
    MUST_EXIST = 'must_exist'
    REMOVE_IF_EXISTS = 'remove_if_exists'


class _SaveLoadMode(enum.Enum):
    PICKLE = 'pickle'
    TORCH = 'torch'


_NO_DEFAULT = object()


def _get_subdict(d, key, create_missing):
    get = getattr(dict, 'setdefault' if create_missing else 'get')
    key = key.split('/')
    for x in key[:-1]:
        d = get(d, x, {})
        msg = (
            'if key is composite (e.g. a/b/c/) then all intermidiate keys must '
            f'correspond to dictionaries; however, the subkey {x} corresponds to the '
            f'value {d} which is {type(d)}'
        )
        assert isinstance(d, dict), msg
    return d, key[-1]


class Experiment:
    def __init__(
        self,
        dir_: PathLike,
        mode: ty.Optional[str] = None,
        *,
        saveload_mode: str = _SaveLoadMode.PICKLE.value,
        writer_kwargs: ty.Optional[ty.Dict[str, ty.Any]] = None,
        debug: bool = False,
    ) -> None:
        dir_ = Path(dir_)
        if debug:
            dir_ = dir_.parent / f'debug_{dir_.name}'
        mode = (
            _Mode(mode)
            if mode
            else _Mode.REMOVE_IF_EXISTS
            if debug
            else _Mode.EXIST_NOT_OK
        )
        saveload_mode = _SaveLoadMode(saveload_mode)

        if mode == _Mode.EXIST_OK:
            pass
        elif mode == _Mode.EXIST_NOT_OK:
            assert not dir_.exists()
        elif mode == _Mode.MUST_EXIST:
            assert dir_.exists()
        elif mode == _Mode.REMOVE_IF_EXISTS:
            if dir_.exists():
                shutil.rmtree(dir_)
        else:
            assert False, '[Unreachable] Invalid mode'
        dir_.mkdir(exist_ok=True)

        self._dir = dir_
        self._debug = debug
        if saveload_mode == _SaveLoadMode.PICKLE:
            self._saver = dump_pickle
            self._loader = load_pickle
        elif saveload_mode == _SaveLoadMode.TORCH:
            try:
                import torch  # type: ignore
            except ImportError as err:
                raise RuntimeError(
                    'If saveload_mode == "torch", then torch must be installed'
                ) from err
            self._saver = torch.save
            self._loader = torch.load
        else:
            assert False, '[Unreachable] Invalid saveload_mode'
        if writer_kwargs is None:
            self.writer = None
        else:
            try:
                from torch.utils.tensorboard import SummaryWriter  # type: ignore
            except ImportError as err:
                raise RuntimeError(
                    'If writer_kwargs is not None, then torch must be installed'
                ) from err
            self.writer = SummaryWriter(self.dir, **writer_kwargs)

    @property
    def dir(self) -> Path:
        return self._dir

    @property
    def _info_path(self) -> Path:
        return self.dir / 'info.json'

    def load_info(self) -> JSON:
        return load_json(self._info_path) if self._info_path.exists() else {}

    def get_info(self, key: str, default: ty.Any = _NO_DEFAULT) -> ty.Any:
        info = self.load_info()
        d, k = _get_subdict(info, key, False)
        return d[k] if default is _NO_DEFAULT else d.get(k, default)

    def set_info(self, key: str, value: ty.Any) -> None:
        info = self.load_info()
        d, k = _get_subdict(info, key, True)
        d[k] = value
        dump_json(info, self._info_path, indent=4)

    def append_info(self, key: str, value: ty.Any) -> None:
        info = self.load_info()
        d, k = _get_subdict(info, key, True)
        d.setdefault(k, []).append(value)
        dump_json(info, self._info_path, indent=4)

    def save_argv(self) -> None:
        self.set_info('command', ' '.join(sys.argv))

    def _get_absolute_path(self, path: PathLike) -> Path:
        path = Path(path)
        assert not path.is_absolute()
        return self.dir / path

    def save(self, value: ty.Any, path: PathLike) -> None:
        path = self._get_absolute_path(path)
        path.parent.mkdir(exist_ok=True, parents=True)
        self._saver(value, path)

    def load(self, path: PathLike) -> None:
        path = self._get_absolute_path(path)
        assert path.exists()
        return self._loader(path)
