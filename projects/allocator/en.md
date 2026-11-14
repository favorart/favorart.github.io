---
title: "allocator: a memory allocator with defragmentation"
summary: "A C++ memory allocator over a fixed arena that can defragment itself, paired with a smart pointer that stays valid when blocks move."
kind: Memory allocator · C++
---

A course project from 2015 (Technosphere, Mail.Ru Group and Lomonosov MSU): a memory allocator that manages one fixed arena by itself instead of calling the system `malloc`.

## How it works

- **No extra memory.** The allocator hands out blocks of a pre-allocated buffer, and its own bookkeeping — a doubly linked list of block descriptors — lives in the same buffer, packed from its end without gaps. Allocation and release take O(1).
- **Defragmentation.** After many allocations and releases the free space breaks into small pieces. The allocator moves live blocks together so the free space becomes one contiguous region again; a block can also be reallocated to a larger size.
- **A smart pointer.** Moving blocks would break raw pointers, so the user works through a `Pointer` class that refers to a block descriptor and is corrected when the block moves.
- **Tests.** The repository has a test program for allocation, release, reallocation and defragmentation.

## Why it matters

Custom allocators are one of the main tools of performance work in C++: fewer system calls, better data locality and predictable memory use. This project shows the mechanics underneath — and the price of moving objects in memory.
