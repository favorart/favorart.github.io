---
title: "Moving to AVX-512 didn't speed anything up"
summary: "Why rewriting NeoML's hot loops from AVX2 to AVX-512 gave no speedup: Intel's frequency \"licenses\", the cost of switching, and Lemire's rule."
source: posts/2026-11-avx512-frequency/index.md
source_lang: ru
source_hash: 8b5e3da9
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
In 2023 I was working at ABBYY on NeoML. It's an open-source ML framework, and it ran production neural-network inference on Windows servers. The code was kept as portable as possible, so the compiler wasn't allowed to vectorize beyond SSE/SSE2.

At some point the team decided to speed up the very hottest spots for specific Xeons. Convolutions, matrix multiplication and vector functions were rewritten by hand in AVX2 and FMA, and some of the convolutions got a JIT via xbyak. The speedup was clear.

When I joined the team, the task sounded logical: since AVX2 gave a nice boost, let's rewrite the same bottlenecks in AVX-512 — the vector is twice as wide. It'll be faster, right?

I rewrote them and measured. Wrong: no speedup.

The reason is Intel's frequency "licenses". When a Xeon core (Skylake-SP / Cascade Lake) executes vector instructions, it drops to a lower frequency ceiling: L0 for regular code, L1 for heavy AVX2, L2 for heavy AVX-512. With dense AVX-512 on many cores, the frequency loss reaches ~40%. Our wide instructions came in a continuous stream inside long loops, and whatever we gained from the wider vector was eaten up by the lower frequency.

You could probably let the compiler insert these instructions where it sees fit, i.e. "sprinkle in a little at a time", but that isn't free either. Switching to another license costs 10–20 µs of running at half speed, and the previous frequency only comes back after ~2 ms. A single stray heavy instruction slows down all the remaining code on that core — which, by the way, runs both of the processor's hyper-threads. Tellingly, GCC and Clang, even with AVX-512 enabled, prefer 256-bit vectors by default (-mprefer-vector-width=256) for exactly this reason.

Where do these rules come from? It all comes down to power and heat. A 512-bit FMA per cycle toggles several times more transistors than scalar code. The energy isn't released across the whole die but in a small area occupied by the vector units, and that turns into a hot spot. Current spikes, voltage sags, and the chip has to raise the voltage to keep the wide units stable. To stay within its power (TDP), current and temperature limits, the processor lowers the frequency in advance, without waiting to overheat. Hence the cost of switching: while the voltage ramps up and the upper halves of the vector registers — normally powered off to save energy — are switched on, the core runs at half speed.

Our team had seen something similar before: on processors with AVX-512, our fast AVX convolution was first disabled and then cut out entirely.

What I took away from this:

- Daniel Lemire's rule: AVX-512 is worth it if the per-cycle gain is well above 2x.
- On newer processors the penalty is probably smaller, so the answer depends on the hardware. Frequency, memory and the nature of the workload are what decide it.
- Measure first, draw conclusions later.

Further reading:

- [Cloudflare Blog: On the dangers of Intel's frequency scaling](https://blog.cloudflare.com/on-the-dangers-of-intels-frequency-scaling/)
- [Travis Downs, Performance Matters: Gathering Intel on Intel AVX-512 Transitions](https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html)
- [Daniel Lemire's blog: AVX-512: when and how to use these new instructions](https://lemire.me/blog/2018/09/07/avx-512-when-and-how-to-use-these-new-instructions)

![Image from the post](cover.jpg)
