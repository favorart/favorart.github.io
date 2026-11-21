---
tagline: "Contribuciones al framework de ML de código abierto de ABBYY"
summary: "Más de cien pull requests integrados entre 2022 y 2024 en el framework de ML en C++ de ABBYY: OpenMP sustituido por un thread pool propio, un motor de memoria rediseñado, inferencia multihilo con pesos compartidos e importación de ONNX."
kind: "Contribuciones de código abierto · C++"
---

[NeoML](https://github.com/neoml-lib/neoml) es el framework de código abierto de ABBYY para deep learning y aprendizaje automático clásico: escrito en C++, funciona en CPU, CUDA, Metal y Vulkan, con bindings para Python e importación de modelos ONNX. Entre finales de 2022 y 2024, como parte de mi trabajo en ABBYY, integré en él más de cien pull requests. Las piezas más grandes: sacar OpenMP de todo el framework en favor de un thread pool propio, rediseñar el motor de memoria y ejecutar la inferencia en muchos hilos que comparten una única copia de los pesos.

## Líneas principales del trabajo

- **Fuera OpenMP, dentro un thread pool propio.** El motor matemático de CPU y los algoritmos clásicos (gradient boosting, SVM, k-means, optimizadores) pasaron al thread pool propio del framework, de modo que la biblioteca controla sus hilos y se comporta igual en todas las plataformas; solo el último pull request eliminó casi dos mil líneas.
- **Memoria.** Un motor de memoria y unos asignadores de pila refactorizados, límites de memoria, estadísticas de pico de memoria, pools de búferes por hilo con un umbral en bytes, transferencia de datos entre hilos y capas que consumen menos memoria (incluidas las de LoRA).
- **Inferencia.** Inferencia distribuida: las copias de una red en varios hilos comparten los pesos en lugar de duplicarlos.
- **Velocidad.** Un paso hacia atrás (backward) de la convolución con menos memoria y menos transposiciones, menos sincronizaciones de CUDA, microoptimizaciones en los kernels de pooling; multiplicación de matrices con MKL JIT en algunas capas (revertida en parte más tarde).
- **Motor CUDA.** Correcciones en los kernels de reducción y en los valores por defecto, protección de LSTM en GPU contra NaN.
- **Modelos y ONNX.** Un codificador transformer con prenormalización, recorte de gradientes; en NeoOnnx: LSTM bidireccional, convolución transpuesta 1D, fusión de la normalización de capa y un optimizador de grafos.
- **Compilación y calidad.** Una compilación compacta para Android e iOS, compilación cruzada para macOS, Visual Studio 2022, CodeQL, nuevas pruebas y cabeceras públicas más limpias.

Cada cambio pasó por revisión y tenía que mantener estable la API pública en todas las plataformas soportadas.
