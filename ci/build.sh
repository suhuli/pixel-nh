#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
cd "$work"
patch=${1:-0001-sailfish-force-sim-swte.patch}
base=https://android.googlesource.com
kernel=91a2acf27c31ecf2af539e9c386779363739f8e6
cc64=8d1806968dbb6ba7fdadb2d2b9dc923cd8e3bba5
cc32=12d95865080233a6c4fc9f8bb3572147f1f10452
fetch() {
  echo "Fetch $1 at $3"
  git init -q "$1"
  git -C "$1" fetch --quiet --depth 1 "$base/$2" "$3"
  git -C "$1" checkout --quiet --detach FETCH_HEAD
  test "$(git -C "$1" rev-parse HEAD)" = "$3"
}
fetch kernel kernel/msm "$kernel"
fetch tc64 platform/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9 "$cc64"
fetch tc32 platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9 "$cc32"
export ARCH=arm64 CROSS_COMPILE="$work/tc64/bin/aarch64-linux-android-" CROSS_COMPILE_ARM32="$work/tc32/bin/arm-linux-androideabi-"
for prefix in "$CROSS_COMPILE" "$CROSS_COMPILE_ARM32"; do
  sed -i '1s|^#!/usr/bin/python$|#!/usr/bin/env python3|' "${prefix}gcc"
  "${prefix}gcc" --version
 done
cd kernel
test -f "$root/$patch"
git apply --check "$root/$patch"
git apply "$root/$patch"
make O="$work/obj" HOSTCC='gcc -fcommon' marlin_defconfig
make O="$work/obj" HOSTCC='gcc -fcommon' -j"$(nproc)" Image.lz4-dtb
boot="$work/obj/arch/arm64/boot"; dest="$root/artifacts"; mkdir -p "$dest"
lz4 -dc "$boot/Image.lz4" | cmp - "$boot/Image"
python3 "$root/ci/verify-dtb.py" "$boot"
cp "$boot/Image.lz4-dtb" "$dest/"
cp "$boot/Image.lz4" "$dest/"
python3 "$root/ci/split_image_lz4_dtb.py" "$dest/Image.lz4-dtb" --output-dir "$dest"
cd "$dest"; sha256sum Image.lz4-dtb Image.lz4 kernel_dtb > SHA256SUMS
printf 'kernel=%s\ngcc64=%s\ngcc32=%s\npatch_sha256=%s\nkernel_release=%s\n' "$kernel" "$cc64" "$cc32" "$(sha256sum "$root/$patch" | cut -d' ' -f1)" "$(cat "$work/obj/include/config/kernel.release")" > manifest.txt
