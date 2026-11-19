# pixel-nh

Headless kernel build experiments for Google Pixel 1 (`sailfish`).

This repository builds the exact Android 8.1 kernel line used by the current
device and applies a small MDSS patch intended to keep a simulated display
active when the physical panel is disconnected.

## Target

- Device: Google Pixel 1 (`sailfish`)
- Kernel: `android-msm-marlin-3.18-oreo-m4`
- Kernel commit: `91a2acf27c31ecf2af539e9c386779363739f8e6`
- Android: 8.1.0 / `OPM4.171019.021.P1`
- Toolchain: AOSP `aarch64-linux-android-4.9`

## Patch

`0001-sailfish-force-sim-swte.patch` forces the sailfish panel into
`SIM_SW_TE_MODE` after device-tree lookup. This avoids real panel reads and
hardware TE waits while retaining an MDSS display that SurfaceFlinger and the
vendor HWC may use.

This is experimental. It does not modify the bootloader and cannot help if the
bootloader stops before loading the kernel.

## Build

Open **Actions** and run the `Build sailfish headless kernel` workflow.

The workflow uploads:

- `Image.lz4-dtb`
- `SHA256SUMS`
- `build.log`

Repack the image into a suitable boot image before flashing. Never flash a bare
`Image.lz4-dtb` directly to `boot_a`.
