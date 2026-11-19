"""Verify appended FDT boundaries and compare with built sailfish DTBs."""
import pathlib
import struct
import sys

boot = pathlib.Path(sys.argv[1])
image = (boot / 'Image.lz4-dtb').read_bytes()
kernel = (boot / 'Image.lz4').read_bytes()
if not kernel or not image.startswith(kernel):
    sys.exit('missing compressed kernel prefix')
pos = len(kernel)
trees = set()
while pos < len(image):
    magic, size = struct.unpack_from('>II', image, pos)
    if magic != 0xd00dfeed or not 40 <= size <= len(image) - pos:
        sys.exit('invalid appended DTB')
    trees.add(image[pos:pos + size]); pos += size
expected = list((boot / 'dts').rglob('*sailfish*.dtb'))
if not expected or any(dt.read_bytes() not in trees for dt in expected):
    sys.exit('missing appended sailfish DTB')
print(f'Verified {len(expected)} sailfish DTB files in image')
