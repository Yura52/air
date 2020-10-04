from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable, Iterable, Iterator, Optional, Union

try:
    from tqdm import tqdm  # type: ignore[code]
except ImportError:
    tqdm = None


class Task:
    def __init__(self, f: Callable) -> None:
        self._f = f
        self._args = None
        self._kwargs = None
        self._called = False

    def __call__(self, *args, **kwargs) -> Union['Task', Any]:
        if self._args is None:
            self._args = args
            self._kwargs = kwargs
            return self
        else:
            assert not self._called and not args and not kwargs
            self._called = True
            return self._f(*self._args, **self._kwargs)


def run_tasks(tasks: Iterable[Task], worker_count: Optional[int]) -> Iterator:
    if worker_count == 0:
        for x in tasks:
            yield x()
    else:
        with ProcessPoolExecutor(worker_count) as executor:
            futures = []
            for x in tasks:
                futures.append(executor.submit(x))
            for x in as_completed(futures):
                yield x.result()


def prun(
    f: Callable,
    args: Iterable,
    worker_count: Optional[int] = None,
    star: bool = False,
    verbose: bool = False,
) -> Iterator:
    tasks = []
    for x in args:
        tasks.append(Task(f)(*x) if star else Task(f)(x))
    results = run_tasks(tasks, worker_count)
    if verbose:
        assert tqdm, 'If verbose is True, then tqdm library must be installed'
        results = tqdm(results)
    return list(results)
