---
tagline: "A fast, dependency-free C++20 writer of VCD waveforms"
summary: "A C++20 writer of VCD waveform files: no allocation per value change and byte-identical output on every OS. A sanitizer audit found heap corruption that 18 green tests had missed."
kind: Library · C++20
---

Value Change Dump (VCD) is the text format in which hardware simulators record how signals change over time; GTKWave and other viewers draw it as waveforms. I ported the Python library [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd) to C++ in 2017. In 2026 I ran it under AddressSanitizer and UndefinedBehaviorSanitizer and found a heap buffer overflow, a null dereference, a throwing destructor and invalid VCD output — all hidden behind 18 passing tests, because the reference file the tests compared against had locked in the wrong output. After the fixes the library has 39 tests, and a rewrite of the hot path made `change()` [2–5 times faster](https://github.com/favorart/vcd-writer/pull/10).

## What is inside

- **The standard, item by item.** Four-state VCD from IEEE 1364-2005 §18.2: header, nested scopes, all 18 variable types, scalar, vector and real values, `$dumpvars`, `$dumpoff` / `$dumpon`; string values as a GTKWave extension. The README has a table of what is supported and what is not.
- **No allocation per change.** Values are formatted into a 64 KiB buffer and written in one call; a benchmark is part of the repository.
- **Validation without side effects.** Names, sizes, values and the date are checked before any state changes, so a failed call leaves no trace in the file; a timestamp in the past throws.
- **Deterministic output behind a small interface.** The file is byte-identical on every platform; the writer's state is hidden behind pimpl, and there are no third-party dependencies.

## Engineering

- CI on Linux, Windows and macOS: GoogleTest and a byte-for-byte comparison with a reference file; a separate job runs everything under the sanitizers.
- Every commit that passes CI gets a semantic version tag and a GitHub Release with prebuilt libraries.
- It plugs into a CMake project with `CPMAddPackage`; the README compares it feature by feature with pyvcd and cpp-vcd-tracer.
