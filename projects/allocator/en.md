---
title: "allocator: a memory allocator with defragmentation"
summary: "A C++17 memory allocator over a fixed arena that can defragment itself, paired with a smart pointer that stays valid when blocks move."
kind: Memory allocator · C++
---

A course project from 2015 (Technosphere, Mail.Ru Group and Lomonosov MSU): a memory allocator that manages one fixed arena by itself instead of calling the system `malloc`. In 2026 the code was reviewed: the bugs were fixed, and the project got real tests, CI and releases.

## How it works

- **No extra memory.** The allocator hands out blocks of a pre-allocated buffer, and its own bookkeeping — a doubly linked list of block descriptors sorted by address — lives in the same buffer, packed from its end without gaps. Allocation is first fit and walks the list, O(blocks); release takes O(1).
- **Defragmentation.** After many allocations and releases the free space breaks into small pieces. `defrag()` slides the live blocks together in one pass, so the free space becomes one contiguous region again; `realloc()` grows or shrinks a block in place when there is room.
- **A smart pointer.** Moving blocks would break raw pointers, so the user works through a `Pointer` class. It remembers the descriptor slot and the block's unique index and finds the block again after it moves; a pointer to a freed block resolves to `nullptr`.

## Engineering

- The 2026 review ran the old tests under AddressSanitizer and UndefinedBehaviorSanitizer and found ten bugs — from writes past the buffer to a pointer resolving to someone else's block; each fix has a regression test.
- GoogleTest suites cover the whole public API, plus a randomized stress test that checks every live block byte by byte against a model.
- CI builds with GCC and Clang on Linux (also under the sanitizers), MSVC on Windows and Apple Clang on macOS, with warnings as errors.
- The README has a benchmark against `malloc`/`free` that shows the price honestly: allocation walks the list and is much slower than `malloc`, while compaction is a single `memmove` pass.
- Every push to `master` that passes CI gets a version tag and a GitHub Release with the header and a static library for Linux, Windows and macOS.

## Why it matters

Custom allocators are one of the main tools of performance work in C++: fewer system calls, better data locality and predictable memory use. This project shows the mechanics underneath — and the price of moving objects in memory.
