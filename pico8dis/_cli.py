import sys
from typing import NoReturn, TextIO
from ._core import extract_data, decompress_lua


def run(stdin: TextIO, stdout: TextIO) -> int:
    js = stdin.read()
    if '_cartdat' in js:
        data = extract_data(js)
    else:
        data = js.encode(encoding='utf8')
    lua = decompress_lua(data)
    stdout.write(lua)
    return 0


def entrypoint() -> NoReturn:
    sys.exit(run(sys.stdin, sys.stdout))
