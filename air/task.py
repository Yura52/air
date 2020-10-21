import typing as ty
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    from tqdm import tqdm  # type: ignore[code]
except ImportError:
    tqdm = None


class Task:
    def __init__(self, f: ty.Callable) -> None:
        self._f = f
        self._args: ty.Optional[tuple] = None
        self._kwargs: ty.Optional[dict] = None
        self._called = False

    def __call__(self, *args, **kwargs) -> ty.Union['Task', ty.Any]:
        if self._args is None:
            self._args = args
            self._kwargs = kwargs
            return self
        else:
            assert not self._called and args is not None and kwargs is not None
            self._called = True
            return self._f(*self._args, **self._kwargs)  # type: ignore


def run_tasks(tasks: ty.Iterable[Task], worker_count: ty.Optional[int]) -> ty.Iterator:
    if worker_count == 0:
        for x in tasks:
            yield x()
    else:
        with ProcessPoolExecutor(worker_count) as executor:
            futures = []
            for task in tasks:
                futures.append(executor.submit(task))
            for future in as_completed(futures):
                yield future.result()


def prun(
    f: ty.Callable,
    args: ty.Iterable,
    worker_count: ty.Optional[int] = None,
    star: bool = False,
    verbose: bool = False,
) -> ty.Iterable:
    tasks = []
    for x in args:
        tasks.append(Task(f)(*x) if star else Task(f)(x))
    results = run_tasks(tasks, worker_count)
    if verbose:
        assert tqdm, 'If verbose is True, then tqdm library must be installed'
        results = tqdm(results, total=len(tasks))
    return list(results)
