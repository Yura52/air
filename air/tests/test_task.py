import random
import time
from multiprocessing import cpu_count

from pytest import mark

import air


def f(x):
    time.sleep(random.random() / 100)
    return x * 2


# DON'T RUN THIS TEST FROM VSCODE (it hangs)
@mark.parametrize('n_workers', [0, cpu_count() * 2])
def test_task(n_workers):
    for star in [False, True]:
        data = range(n_workers * 2)
        if star:
            data = ((x,) for x in data)
        assert (
            set(air.prun(f, data, n_workers, star))
            == set(range(0, n_workers * 2 * 2, 2))
        )
