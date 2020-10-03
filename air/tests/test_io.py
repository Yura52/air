import tempfile
from pathlib import Path

import air.io


def test_io():
    data = {'a': ['b', 1], 'c': {'d': 2}, 'e': None}
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / 'whatever'

        air.io.dump_pickle(data, path)
        assert air.io.load_pickle(path) == data

        air.io.dump_json(data, path)
        assert air.io.load_json(path) == data

        air.io.dump_jsonl([data], path)
        assert air.io.load_jsonl(path) == [data]

        air.io.dump_jsonl([data], path)
        air.io.extend_jsonl([data], path)
        assert air.io.load_jsonl(path) == [data, data]
