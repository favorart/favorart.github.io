---
title: "allocator: un asignador de memoria con desfragmentación"
summary: "Un asignador de memoria en C++17 sobre una arena fija capaz de desfragmentarse, acompañado de un puntero inteligente que sigue siendo válido cuando los bloques se mueven."
kind: Asignador de memoria · C++
---

Un proyecto de curso de 2015 en Technosphere, el programa de Mail.Ru Group y la Universidad Estatal de Moscú (MSU): un asignador de memoria que gestiona por sí mismo una arena fija en lugar de llamar al `malloc` del sistema. En 2026 el código pasó por una revisión: se corrigieron los errores y el proyecto recibió pruebas de verdad, CI y versiones publicadas.

## Cómo funciona

- **Sin memoria adicional.** El asignador entrega bloques de un búfer reservado de antemano, y su propia contabilidad —una lista doblemente enlazada de descriptores de bloque, ordenada por dirección— vive en ese mismo búfer, empaquetada desde el final sin huecos. La asignación recorre la lista hasta el primer hueco que sirva, O(número de bloques); liberar cuesta O(1).
- **Desfragmentación.** Tras muchas asignaciones y liberaciones, el espacio libre se fragmenta en trozos pequeños. `defrag()` junta los bloques vivos en una sola pasada para que el espacio libre vuelva a ser una única región contigua; `realloc()` agranda o achica un bloque en su sitio cuando hay espacio.
- **Un puntero inteligente.** Mover bloques invalidaría los punteros crudos, así que el usuario trabaja a través de una clase `Pointer`. Esta recuerda la posición del descriptor y el índice único del bloque, y vuelve a encontrarlo después de que se mueve; un puntero a un bloque liberado devuelve `nullptr`.

## Ingeniería

- La revisión de 2026 ejecutó las pruebas antiguas con AddressSanitizer y UndefinedBehaviorSanitizer y encontró diez errores —desde escrituras fuera del búfer hasta un puntero que encontraba el bloque de otro—; cada corrección tiene su prueba de regresión.
- Las pruebas con GoogleTest cubren toda la API pública, además de una prueba de estrés aleatoria que compara byte a byte cada bloque vivo con un modelo.
- La CI compila con GCC y Clang en Linux (también con los sanitizers), con MSVC en Windows y con Apple Clang en macOS, y trata las advertencias como errores.
- El README incluye un benchmark frente a `malloc`/`free` que muestra el precio sin rodeos: la asignación recorre la lista y es mucho más lenta que `malloc`, mientras que la compactación es una sola pasada de `memmove`.
- Cada push a `master` que pasa la CI recibe una etiqueta de versión y una GitHub Release con el archivo de cabecera y una biblioteca estática para Linux, Windows y macOS.

## Por qué es importante

Los asignadores personalizados son una de las herramientas principales para optimizar el rendimiento en C++: menos llamadas al sistema, mejor localidad de los datos y un uso de memoria predecible. Este proyecto muestra la mecánica que hay debajo y el precio de mover objetos en memoria.
