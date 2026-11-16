"""makefun-ai-excited: write the entry image to /output/entry.png.

The image is the entry.png beside this file: a colossal paper airplane
soaring between skyscrapers at sunset, three real jets trailing aurora
ribbons behind it. The program only copies bytes, so it is deterministic
(same output on every run) and uses no network.
"""

import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
DST = os.path.join(OUT_DIR, "entry.png")
MAX_BYTES = 1048576  # the gate's 1 MiB cap
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_magic(path):
    with open(path, "rb") as f:
        head = f.read(8)
    assert head.startswith(JPEG_MAGIC) or head.startswith(PNG_MAGIC), \
        "entry.png is neither a JPEG nor a PNG"


def main():
    check_magic(SRC)
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    assert sha256(SRC) == sha256(DST), "output bytes differ from entry.png"
    size = os.path.getsize(DST)
    assert size <= MAX_BYTES, f"entry.png is {size} bytes, over the 1 MiB cap"
    print(f"wrote {DST} ({size} bytes)")


if __name__ == "__main__":
    main()
