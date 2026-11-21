---
tagline: "A self-defragmenting allocator with relocatable pointers"
summary: "A C++17 allocator with no side memory: defrag() compacts at 6.4 GB/s and a Pointer follows moved blocks. The price, measured: alloc() is about 140 times slower than malloc."
kind: Memory allocator · C++
---

A course project from 2015 (Technosphere, Mail.Ru Group and Lomonosov MSU): an allocator over one fixed buffer that keeps its own bookkeeping inside that buffer — data grows from the start, block descriptors from the end. Because `defrag()` moves blocks, the user holds a `Pointer` that finds its block again by a unique index. In 2026 sanitizers and a code review found 13 bugs in it, from writes past the buffer to a pointer resolving to someone else's block; each fix has a regression test.

## How it works

- **No side memory.** The descriptors form a doubly linked list sorted by address, packed at the end of the buffer without gaps. Allocation is first fit and walks the list, O(blocks); release takes O(1).
- **Defragmentation.** `defrag()` slides the live blocks together in one pass, so the free space becomes one region again; `realloc()` grows or shrinks a block in place when there is room.
- **A smart pointer.** `Pointer` remembers the descriptor slot and the block's index and finds the block again after it moves; a pointer to a freed block resolves to `nullptr`.
- **Self-checks.** `check()` verifies every invariant of the arena, `dump()` prints its map.

## The price, measured

The README benchmark shows it honestly: allocation takes 4.6 µs against 33 ns for `malloc`, because it walks the list; compaction runs at 6.4 GB/s of live data, and dereferencing a `Pointer` with a cached slot costs 2.3 ns.

## Engineering

- GoogleTest suites over the whole public API, a randomized stress test that checks every live block byte by byte against a model, and a libFuzzer target; the stress tests and the fuzzer call `check()` after every operation.
- CI with GCC and Clang on Linux (also under AddressSanitizer and UndefinedBehaviorSanitizer), MSVC on Windows and Apple Clang on macOS, warnings as errors; every green push to `master` gets a version tag and a GitHub Release.
