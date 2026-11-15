---
title: "b-tree: a key-value store on a B-tree in C"
summary: "An on-disk key-value store written from scratch in C: a B-tree over fixed-size pages, variable-length keys and values, an LRU page cache and a write-ahead journal with crash recovery."
kind: Storage engine · C
---

A small embedded database written in 2015 as a course project at Technosphere (Mail.Ru Group and Lomonosov MSU). The task was to build, from scratch, the storage layer that real databases have underneath: a key-value store behind a given C API (`dbcreate`, `dbopen`, insert, select, delete, sync, close) that keeps its data in a single file. In 2026 the project was brought back to life: the unfinished deletion and journal recovery were completed and everything was covered by tests.

## How it works

- **B-tree over pages.** The file is split into fixed-size pages (4 KB by default); every tree node is a page. Keys and values of variable length are stored right in the nodes, up to 1/8 of a page per entry.
- **Splits and rebalancing.** Full pages are split on the way down, in one pass; sequential inserts split at the insertion point, so the pages stay well filled. On delete, underfull pages are merged with a sibling or borrow entries from it.
- **Free-space map.** Service pages keep a bitmap of free pages, so deleted pages are reused.
- **LRU cache.** Recently used pages stay in memory (16 MB by default); dirty pages are written back on eviction — all of them at once, so the file always holds a consistent tree.
- **Journal.** Every change goes first to a write-ahead log with checksummed records; on open, the records after the last checkpoint are replayed, and a record torn by a crash is ignored.
- **Configuration.** File size, page size and cache size are set when the database is created.

## Engineering

- Plain C99 and POSIX, no dependencies, built with Make; Windows is not supported.
- cmocka tests: unit tests of the modules, random operations checked against a reference model, crash recovery in a child process and the worst-case workloads; they also run under AddressSanitizer and UndefinedBehaviorSanitizer.
- CI on Linux (gcc and clang, plain and with the sanitizers) and macOS; the benchmark runs on every push to `master`.
- Every push to `master` that passes CI gets a version tag and a GitHub Release with the library for Linux and macOS.

## Why it matters

The project touches the core questions of every storage engine: page layout, node splits and merges, caching and durability. It is a direct path from the textbook B-tree to the way SQLite or InnoDB are built.
