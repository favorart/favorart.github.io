---
title: "b-tree: a key-value store on a B-tree in C"
summary: "An on-disk key-value store written from scratch in C: a B-tree over fixed-size pages, keys and values of any length, an LRU page cache and a journal."
kind: Storage engine · C
---

A small embedded database written in 2015 for the systems-programming course at Technosphere (Mail.Ru Group and Lomonosov MSU). The task was to build, from scratch, the storage layer that real databases have underneath: a key-value store with a `dbopen`-like interface (`put`, `get`, `delete`, `sync`, `close`) that keeps its data in a single file.

## How it works

- **B-tree over pages.** The file is split into fixed-size pages (4 KB by default); every tree node is a page. Keys and values may be of any length.
- **Free-space map.** Service pages keep a bitmap of free pages, so deleted pages are reused.
- **LRU cache.** Recently used pages stay in memory (16 MB by default); dirty pages are written back on eviction.
- **Journal.** Changes go to a log first, so the database can be restored after a crash.
- **Configuration.** File size, page size and cache size are set when the database is created.

## Why it matters

The project touches the core questions of every storage engine: page layout, node splits and merges, caching and durability. It is a direct path from the textbook B-tree to the way SQLite or InnoDB are built.
