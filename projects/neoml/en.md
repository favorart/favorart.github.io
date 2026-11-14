---
title: "NeoML: contributions to ABBYY's machine-learning framework"
summary: "Over a hundred merged pull requests to NeoML, ABBYY's open-source C++ framework for deep learning and classic ML: performance, memory, CUDA and ONNX import."
kind: Open-source contributions · C++
---

[NeoML](https://github.com/neoml-lib/neoml) is ABBYY's open-source machine-learning framework: neural networks and classic algorithms, written in C++, running on CPU, CUDA, Metal and Vulkan, with Python bindings and ONNX model import. From 2022 to 2024, as part of my work at ABBYY, I merged more than a hundred pull requests into it.

## Main threads of the work

- **OpenMP out, own thread pool in.** I moved the CPU math engine and the classic algorithms (gradient boosting, SVM, k-means, optimizers) from OpenMP to the framework's own thread pool, so the library controls its threads and runs the same on every platform.
- **Memory.** I refactored the memory engine and the stack allocators, added memory limits, peak-memory statistics, buffer pools per thread and data transfer between threads, and made layers use less memory (including LoRA layers).
- **Speed.** Faster convolution backward pass, MKL JIT matrix multiplication, a matrix multiplier tuned to L1/L2 cache sizes, fewer CUDA synchronizations, micro-optimizations in pooling kernels.
- **CUDA engine.** Fixes in reduction kernels, shared buffer initialization and default values.
- **Models.** A transformer encoder with pre-normalization, gradient clipping, distributed inference; in NeoOnnx — bidirectional LSTM, 1D transposed convolution, layer-normalization fusion and a graph optimizer.
- **Builds and quality.** A compact build for Android and iOS, cross-compilation for macOS, the move to Visual Studio 2022, CodeQL checks, new tests and cleaner public headers.

## Why it matters

This is production code that other teams and outside users build on: every change went through review, had to keep the API stable and work on every supported platform.
