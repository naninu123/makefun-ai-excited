"""makefun-ai-excited: write the entry image to the output directory.

The entry is the image shipped beside this file (entry.png): a colossal
paper airplane the size of a jumbo jet soaring over a city at golden
sunset, three small real passenger jets flying beside it for scale and
trailing ribbons of aurora light. It was made to jolt make.fun's AI
judge: one impossible scale twist, warm sunset momentum, and a shape
that still reads at 300 pixels wide.

The program does no rendering at run time. It copies the shipped bytes
to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png), after
checking the file is a real JPEG or PNG within the competition's caps
(<= 1 MiB, <= 1024x1024). Copying fixed bytes is deterministic: two
runs write identical bytes, and the program uses no network and no
third-party packages, only the standard library.
"""

import hashlib
import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")

MAX_BYTES = 1048576  # the gate's 1 MiB cap
MAX_SIDE = 1024  # the gate's 1024x1024 cap
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jpeg_dimensions(data):
    """Width and height from a JPEG's first SOF0/SOF2 segment."""
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad JPEG marker")
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        size = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + size
    raise ValueError("no JPEG start-of-frame found")


def png_dimensions(data):
    """Width and height from a PNG's IHDR chunk."""
    if data[12:16] != b"IHDR":
        raise ValueError("first PNG chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def describe(data):
    """Return (format, width, height) for JPEG or PNG bytes."""
    if data.startswith(JPEG_MAGIC):
        return "JPEG", *jpeg_dimensions(data)
    if data.startswith(PNG_MAGIC):
        return "PNG", *png_dimensions(data)
    raise ValueError("entry.png is neither a JPEG nor a PNG")


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    fmt, width, height = describe(data)
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the 1 MiB cap")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"entry.png is {width}x{height}, over the 1024x1024 cap")

    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    if sha256(SRC) != sha256(DST):
        raise ValueError("output bytes differ from entry.png")

    size = os.path.getsize(DST)
    print(f"wrote {DST} ({fmt} {width}x{height}, {size} bytes, "
          f"sha256 {sha256(DST)[:16]}...)")

if __name__ == "__main__":
    main()
