---
tagline: "An on-disk B-tree key-value store in C with a journal"
summary: "A single-file key-value store in plain C: B-tree pages, an LRU cache and a checksummed journal. Crash recovery is tested by killing a child process; worst cases are measured."
kind: Storage engine · C
---

An embedded key-value store I wrote in 2015 at Technosphere (Mail.Ru Group and Lomonosov MSU) behind a given C API, and finished in 2026. Every page of the file is a B-tree node. The cache writes all dirty pages at once, so the file always holds a consistent tree, and replaying the journal after a process crash brings back every committed change. Splitting a full page at the insertion point keeps sequential inserts at 68% page fill.

## How it works

- **B-tree over pages.** Fixed-size pages (4 KB by default); keys and values of variable length are stored right in the nodes, up to 1/8 of a page per entry. Full pages are split on the way down in one pass; on delete, underfull pages are merged with a sibling or borrow entries from it.
- **Free-space map.** Service pages keep a bitmap of free pages, so deleted pages are reused.
- **LRU cache.** Recently used pages stay in memory (16 MB by default); evicting a dirty page writes all of them and calls `fsync`.
- **Journal.** Every change goes first to a log with checksummed records; on open, the records after the last checkpoint are replayed, and a record torn by a crash is ignored.
- **Diagnostics.** `db_check` verifies the tree, `db_stats` reports its shape and fill, `db_trace` logs operations at four levels.

## Engineering

- Plain C99 and POSIX, no dependencies, built with Make.
- cmocka tests: unit tests of the modules, random operations checked against a reference model, crash recovery in a child process and worst-case workloads; all of them also run under AddressSanitizer and UndefinedBehaviorSanitizer.
- A benchmark in the README: when the tree fits in the cache, about 186 thousand random inserts and 594 thousand lookups per second.
- CI on Linux (gcc and clang, plain and with the sanitizers) and macOS; every push to `master` that passes CI gets a version tag and a GitHub Release.

## Limitations

The journal protects against a crash of the process, not against a power loss; the database is used by one process at a time; it is a B-tree, not a B+-tree.
