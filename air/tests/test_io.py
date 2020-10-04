import tempfile
from pathlib import Path

import air


def test_io():
    data = {'a': ['b', 1], 'c': {'d': 2}, 'e': None}
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / 'whatever'

        air.dump_pickle(data, path)
        assert air.load_pickle(path) == data

        air.dump_json(data, path)
        assert air.load_json(path) == data

        air.dump_jsonl([data], path)
        assert air.load_jsonl(path) == [data]

        air.dump_jsonl([data], path)
        air.extend_jsonl([data], path)
        assert air.load_jsonl(path) == [data, data]
