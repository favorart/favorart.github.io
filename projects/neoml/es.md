---
title: "NeoML: contribuciones al framework de aprendizaje automático de ABBYY"
summary: "Más de cien pull requests integrados en NeoML, el framework de código abierto en C++ de ABBYY para deep learning y ML clásico: rendimiento, memoria, CUDA e importación de ONNX."
kind: Contribuciones de código abierto · C++
---

[NeoML](https://github.com/neoml-lib/neoml) es el framework de aprendizaje automático de código abierto de ABBYY: redes neuronales y algoritmos clásicos, escrito en C++, que funciona en CPU, CUDA, Metal y Vulkan, con bindings para Python e importación de modelos ONNX. Entre 2022 y 2024, como parte de mi trabajo en ABBYY, integré en él más de cien pull requests.

## Líneas principales del trabajo

- **Fuera OpenMP, dentro un thread pool propio.** Pasé el motor matemático de CPU y los algoritmos clásicos (gradient boosting, SVM, k-means, optimizadores) de OpenMP al thread pool propio del framework, de modo que la biblioteca controla sus hilos y se comporta igual en todas las plataformas.
- **Memoria.** Refactoricé el motor de memoria y los asignadores de pila, añadí límites de memoria, estadísticas de pico de memoria, un umbral en bytes para los pools de búferes de cada hilo y transferencia de datos entre hilos, y reduje el consumo de memoria de las capas (incluidas las capas LoRA).
- **Velocidad.** Un paso hacia atrás (backward) más rápido en la convolución, multiplicación de matrices con MKL JIT en algunas capas (revertida en parte más tarde), menos sincronizaciones de CUDA y microoptimizaciones en los kernels de pooling.
- **Motor CUDA.** Correcciones en los kernels de reducción y en los valores por defecto, protección de LSTM en GPU contra NaN e inicializaciones defensivas.
- **Modelos.** Un codificador transformer con prenormalización, recorte de gradientes, inferencia distribuida; en NeoOnnx: LSTM bidireccional, convolución transpuesta 1D, fusión de la normalización de capa y un optimizador de grafos.
- **Compilación y calidad.** Una compilación compacta para Android e iOS, compilación cruzada para macOS, la migración a Visual Studio 2022, comprobaciones de CodeQL, nuevas pruebas y cabeceras públicas más limpias.

## Por qué es importante

Es código de producción sobre el que construyen otros equipos y usuarios externos: cada cambio pasó por revisión, tenía que mantener estable la API y funcionar en todas las plataformas soportadas.
