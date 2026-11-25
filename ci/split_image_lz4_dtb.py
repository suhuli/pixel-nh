#!/usr/bin/env python3
import argparse
import struct
from pathlib import Path


FDT_MAGIC = b"\xd0\x0d\xfe\xed"
LZ4_FRAME_MAGIC = b"\x04\x22\x4d\x18"
LZ4_LEGACY_MAGIC = b"\x02\x21\x4c\x18"


def parse_dtb_chain(data: bytes, start: int):
    pos = start
    while pos < len(data):
        if data[pos : pos + 4] != FDT_MAGIC or pos + 8 > len(data):
            return None
        size = struct.unpack_from(">I", data, pos + 4)[0]
        if size < 40 or size > len(data) - pos:
            return None
        pos += size
    return pos if pos == len(data) else None


def main():
    parser = argparse.ArgumentParser(
        description="Split an Android Image.lz4-dtb into Image.lz4 and kernel_dtb."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    data = args.input.read_bytes()
    if not (data.startswith(LZ4_FRAME_MAGIC) or data.startswith(LZ4_LEGACY_MAGIC)):
        raise SystemExit("input does not start with an LZ4 frame")

    candidates = []
    pos = data.find(FDT_MAGIC)
    while pos >= 0:
        if parse_dtb_chain(data, pos) == len(data):
            candidates.append(pos)
        pos = data.find(FDT_MAGIC, pos + 1)

    if not candidates:
        raise SystemExit("no valid appended DTB chain found")

    boundary = candidates[0]
    count = 0
    pos = boundary
    while pos < len(data):
        size = struct.unpack_from(">I", data, pos + 4)[0]
        pos += size
        count += 1

    output_dir = args.output_dir or args.input.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "Image.lz4"
    dtb_path = output_dir / "kernel_dtb"
    image_path.write_bytes(data[:boundary])
    dtb_path.write_bytes(data[boundary:])

    print(f"boundary={boundary}")
    print(f"dtb_count={count}")
    print(f"image_lz4={image_path} size={image_path.stat().st_size}")
    print(f"kernel_dtb={dtb_path} size={dtb_path.stat().st_size}")


if __name__ == "__main__":
    main()
