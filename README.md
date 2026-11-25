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
`SIM_SW_TE_MODE` after device-tree lookup. If the bootloader selects one of
Qualcomm's `qcom,mdss_dsi_sim_*` panels, the patch replaces it with the
EA8064TG 1080x1920 command-mode panel while retaining software TE. This avoids
real panel reads and hardware TE waits while retaining an MDSS display that
SurfaceFlinger and the vendor HWC may use.

This is experimental. It does not modify the bootloader and cannot help if the
bootloader stops before loading the kernel.

## Build

Open **Actions** and run the `Build sailfish headless kernel` workflow.

The workflow uploads:

- `Image.lz4-dtb`
- `Image.lz4`
- `kernel_dtb`
- `SHA256SUMS`
- `build.log`

`Image.lz4` and `kernel_dtb` are provided separately so they can be packed into
boot image header v0 correctly. Never flash a bare kernel component directly
to `boot_a`.

## CI scope and verification

The workflow fetches the exact upstream kernel and both GCC commits. It uses the
original panel node, not a new virtual display. A successful build verifies the
LZ4 payload and that the compiled sailfish DTBs were appended; it does **not**
prove that Android, HWC, ADB, or scrcpy works without the panel. Build logs are
available even on compilation failure. CI needs no personal token, device
backup, boot image, or signing key. The downloadable image is a **kernel**, not
a flashable boot image. Repack separately with a matching device boot image.
