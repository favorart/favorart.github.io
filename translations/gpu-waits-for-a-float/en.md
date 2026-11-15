---
title: "How can a single float slow down GPU training?"
summary: "A single scalar sent to the GPU with a synchronous cudaMemcpy stalls the whole training pipeline. Why that happens, and how NeoML avoids the stalls by passing the number by value."
source: posts/2026-11-gpu-waits-for-a-float/index.md
source_lang: ru
source_hash: f24792e0
translated: 2026-11-15
translator: Claude
reviewed: 2026-11-15
---
How can a single float slow down GPU training?

You put a powerful GPU in a server so that matrices, convolutions and gradients fly. It hurts when computations on huge matrices just sit there waiting. I fixed this problem in NeoML, ABBYY's open-source ML library (my [previous post](/writing/avx512-frequency/) was about it too).

A GPU is a separate mini-computer with its own memory, and it can't see the program's RAM: everything it needs for computing has to be delivered over the bus.

When training neural networks, the CPU barely computes anything itself — it queues up tasks for the GPU. It enqueues one in a couple of microseconds and runs on without waiting for the result. The GPU executes tasks strictly in order. If one writes its result to device memory and the next one reads it, there's nothing to wait for: by the time the second starts, the data is already there. In a healthy program the CPU runs far ahead, and the GPU's task queue never runs dry.

Now suppose a task needs a number from the CPU, just 4 bytes. The bus bandwidth has nothing to do with it: those bytes fly across instantly. It's the trip itself that's expensive.

CUDA's basic copy function, cudaMemcpy, is synchronous: it first waits until the GPU has finished everything enqueued earlier, and only then copies. The ordering matters: tasks in the queue may still be reading that location on the device, and they need the old value.

Then there's a layover. The bytes are carried over the bus by a separate unit of the GPU, the DMA engine. It can only pick them up from pinned RAM — memory the OS won't swap out to disk or move around. So the driver first copies the number into its own pinned staging buffer, and only from there does it travel to the device.

Bottom line: the CPU stalls until the GPU drains the queue, then two transfers, then the GPU sits idle while the CPU refills the queue. NVIDIA has a measurement: a kernel that runs for 2.9 µs. If the CPU doesn't wait, it comes out at 3.8 µs per kernel. If it waits after each one — 9.6. That's 2.5× slower, and that's before any copying.

You can avoid waiting: cudaMemcpyAsync enqueues the copy as just another task. But then the number has to live in pinned RAM and stay unchanged until the queue gets to it. Allocating such memory is slow, and it's taken away from the OS, so you can't grab a fresh buffer for every number. You need a pool of slots and bookkeeping of which ones the GPU has already read. A whole subsystem for 4 bytes.

NeoML didn't have one. Almost every method took scalars as a pointer into device memory, and cudaMemcpy was what put them there. The machine epsilon in a loss function, the ReLU threshold in MobileNet blocks, the gradient clipping bounds in the optimizer, any coefficient at all — they rode to the device with a full pipeline stall. On every training step.

There turned out to be a workaround: kernel arguments are passed by value, inside the launch command itself. The number is written into the command at enqueue time — no buffer, no trip. Wherever the coefficient comes from — by value from host memory or by pointer from device memory — it's known by the time the kernel starts. No stalls in either case.

The [PR](https://github.com/neoml-lib/neoml/pull/1070) that helps the GPU stop waiting has itself been waiting its turn since 2024.

Have you ever had to hunt down what your code was waiting for?

\#CUDA #GPU #ML #performance

Further reading:

* NVIDIA, CUDA Runtime API: API synchronization behavior — which copies wait for the queue and which don't https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html
* NVIDIA, How to Optimize Data Transfers in CUDA C/C++ — pinned memory and the cost of small transfers https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/
* NVIDIA, Getting Started with CUDA Graphs — where the 2.9 / 3.8 / 9.6 µs figures come from https://developer.nvidia.com/blog/cuda-graphs/
* PyTorch Performance Tuning Guide https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html

![Image from the post](cover.jpg)
