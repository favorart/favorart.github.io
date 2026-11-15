---
title: "vcd-writer: a C++20 library for VCD waveform files"
summary: "A dependency-free C++20 port of pyvcd that writes Value Change Dump files (IEEE 1364-2005) without allocating on every value change."
kind: Library · C++20
---

Value Change Dump (VCD) is the text format in which hardware simulators record how signals change over time; viewers such as GTKWave draw it as waveforms. **vcd-writer** writes such files from C++ code: a simulator, an emulator or a test bench registers variables in nested scopes and reports their changes, and the library produces a VCD file that any waveform viewer opens.

It started in 2017 as a port of the Python library [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd) and in 2026 was reworked into a modern library.

## What is inside

- **The standard, checked item by item.** Four-state VCD from IEEE 1364-2005 §18.2: header (`$date`, `$version`, `$timescale`, `$comment`), nested scopes, all 18 variable types, scalar, vector, real and string values, `$dumpvars`, `$dumpoff` / `$dumpon`. The README has a table of what is supported and what is not.
- **No allocation per change.** Values go into a 64 KiB output buffer; a benchmark is part of the repository.
- **Validation without side effects.** Names, sizes, values and the date are checked before any state changes, so a failed call leaves no trace in the file; a timestamp in the past throws.
- **Deterministic output.** The file is byte-identical on every platform.
- **A clean interface.** The writer's state is hidden behind pimpl; there are no third-party dependencies.

## Engineering

- CI on Linux, Windows and macOS: GoogleTest unit tests and a byte-for-byte comparison with a reference file; a separate Linux job runs them under AddressSanitizer and UndefinedBehaviorSanitizer.
- Every commit that passes CI gets a semantic version tag and a GitHub Release with prebuilt libraries.
- It plugs into a CMake project with `CPMAddPackage`; a plain Makefile build is there too.
- The README compares it feature by feature with pyvcd and cpp-vcd-tracer.

## Why it matters

A small library is a good place to show the whole engineering cycle: a standard read closely, an API that is hard to misuse, measured performance and a release process that needs no manual steps.
