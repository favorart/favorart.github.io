---
tagline: "Contributions to ABBYY's open-source C++ ML framework"
summary: "Over a hundred merged pull requests to ABBYY's C++ ML framework in 2022–2024: OpenMP replaced by its own thread pool, a reworked memory engine, multi-threaded inference on shared weights, ONNX import."
kind: Open-source contributions · C++
---

[NeoML](https://github.com/neoml-lib/neoml) is ABBYY's open-source framework for deep learning and classic machine learning: C++, running on CPU, CUDA, Metal and Vulkan, with Python bindings and ONNX model import. From late 2022 to 2024, as part of my work at ABBYY, I merged more than a hundred pull requests into it. The largest pieces: taking OpenMP out of the whole framework in favour of its own thread pool, reworking the memory engine, and running inference on many threads that share one copy of the weights.

## Main threads of the work

- **OpenMP out, own thread pool in.** The CPU math engine and the classic algorithms (gradient boosting, SVM, k-means, optimizers) moved to the framework's own thread pool, so the library controls its threads and behaves the same on every platform; the final pull request alone deleted almost two thousand lines.
- **Memory.** A refactored memory engine and stack allocators, memory limits, peak-memory statistics, per-thread buffer pools with a byte threshold, data transfer between threads, and leaner layers (including LoRA).
- **Inference.** Distributed inference: copies of a network in several threads share the weights instead of duplicating them.
- **Speed.** A convolution backward pass with less memory and fewer transpositions, fewer CUDA synchronizations, micro-optimizations in pooling kernels; MKL JIT matrix multiplication in some layers (later partly rolled back).
- **CUDA engine.** Fixes in reduction kernels and default values, NaN avoidance in LSTM on GPU.
- **Models and ONNX.** A transformer encoder with pre-normalization, gradient clipping; in NeoOnnx — bidirectional LSTM, 1D transposed convolution, layer-normalization fusion and a graph optimizer.
- **Builds and quality.** A compact Android/iOS build, macOS cross-compilation, Visual Studio 2022, CodeQL, new tests and cleaner public headers.

Every change went through review and had to keep the public API stable on every supported platform.
