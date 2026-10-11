from pathlib import Path
import sys
from argparse import ArgumentParser
from typing import NoReturn, TextIO
from ._core import convert_sprite, extract_data, decompress_lua


def run(stdin: TextIO) -> int:
    parser = ArgumentParser()
    parser.add_argument('-o', '--output', default='game')
    args = parser.parse_args(sys.argv[1:])
    out = Path(args.output)
    out.mkdir(exist_ok=True)

    js = stdin.read()
    if '_cartdat' in js:
        data = extract_data(js)
    else:
        data = js.encode(encoding='utf8')
    lua = decompress_lua(data)
    (out / 'code.lua').write_text(lua)
    with (out / 'sprites.png').open('wb') as stream:
        convert_sprite(data, stream)

    return 0


def entrypoint() -> NoReturn:
    sys.exit(run(sys.stdin))
