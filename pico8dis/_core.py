
from dataclasses import dataclass
import struct


def extract_data(js: str) -> bytes:
    raw_arr = js.split('var _cartdat=[')[1].split(']')[0]
    raw_arr = raw_arr.replace('\n', '')
    arr = [int(b) for b in raw_arr.split(',')]
    data = bytes(arr)
    assert len(data) == 0x8000
    return data


def decompress_lua(data: bytes) -> str:
    return decompress_lua_bin(data).decode(encoding='utf8')


def decompress_lua_bin(data: bytes) -> bytearray:
    assert len(data) == 0x8000
    data = data[0x4300:]
    assert data[:4] == b'\0pxa'
    raw_len, _comp_len = struct.unpack('>HH', data[4:8])
    reader = Reader(data=data)
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


def main():
    js = open("attackaxis.js").read()
    data = extract_data(js)
    open('data', 'wb').write(data)
