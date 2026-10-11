
from dataclasses import dataclass
import struct
from typing import BinaryIO
import zlib


def extract_data(js: str) -> bytes:
    raw_arr = js.split('var _cartdat=[')[1].split(']')[0]
    raw_arr = raw_arr.replace('\n', '')
    arr = [int(b) for b in raw_arr.split(',')]
    data = bytes(arr)
    assert len(data) == 0x8000
    return data


def convert_sprite(data: bytes, out: BinaryIO) -> None:
    palette = bytes.fromhex('0000001d2b537e2553008751ab52365f574fc2c3c7fff1e8ff004dffa300ffec2700e43629adff83769cff77a8ffccaa')
    pixels = bytes((data[y*64+x//2] >> (4*(x % 2))) & 15 for y in range(128) for x in range(128))
    out.write(b'\x89PNG\r\n\x1a\n')
    out.write(png_chunk(b'IHDR', struct.pack('>IIBBBBB', 128, 128, 8, 3, 0, 0, 0)))
    out.write(png_chunk(b'PLTE', palette))
    pixels = b''.join(b'\0' + pixels[y*128:(y+1)*128] for y in range(128))
    out.write(png_chunk(b'IDAT', zlib.compress(pixels)))
    out.write(png_chunk(b'IEND', b''))


def png_chunk(tag, data):
    prefix = struct.pack('>I', len(data))
    suffix = struct.pack('>I', zlib.crc32(tag+data) & 0xffffffff)
    return prefix + tag + data + suffix


def decompress_lua(data: bytes) -> str:
    return _decompress_lua_bin(data).decode(encoding='utf8')


def _decompress_lua_bin(data: bytes) -> bytearray:
    assert len(data) == 0x8000
    data = data[0x4300:]
    assert data[:4] == b'\0pxa'
    raw_len, comp_len = struct.unpack('>HH', data[4:8])
    reader = Reader(data=data[:comp_len])
    out = bytearray()
    mtf = list(range(256))

    while len(out) < raw_len:
        if reader.read(1):
            u = 0
            while reader.read(1):
                u += 1
                assert u <= 4
            idx = reader.read(4+u) + ((1 << u)-1)*16
            assert idx < 256
            v = mtf.pop(idx)
            out.append(v)
            mtf.insert(0, v)
        else:
            width = (5 if reader.read(1) else 10) if reader.read(1) else 15
            d = reader.read(width)
            if width == 10 and d == 0:
                while True:
                    v = reader.read(8)
                    if v == 0:
                        break
                    out.append(v)
            else:
                distance = d+1
                length = 3
                while True:
                    v = reader.read(3)
                    length += v
                    if v != 7:
                        break
                assert distance <= len(out)
                for _ in range(length):
                    out.append(out[-distance])
        assert len(out) <= raw_len
    return out


@dataclass
class Reader:
    data: bytes
    _bitpos: int = 64

    def read(self, n: int) -> int:
        v = 0
        for i in range(n):
            v |= ((self.data[self._bitpos//8] >> (self._bitpos % 8)) & 1) << i
            self._bitpos += 1
        return v
