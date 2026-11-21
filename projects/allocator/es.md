---
tagline: "Asignador que se desfragmenta solo, con punteros reubicables"
summary: "Un asignador en C++17 sin memoria adicional: defrag() compacta a 6,4 GB/s y un Pointer sigue a los bloques que se mueven. El precio, medido: alloc() es unas 140 veces más lento que malloc."
kind: "Asignador de memoria · C++"
---

Un proyecto de curso de 2015 (Technosphere, el programa de Mail.Ru Group y la Universidad Estatal de Moscú, MSU): un asignador sobre un único búfer fijo que guarda su propia contabilidad dentro de ese mismo búfer —los datos crecen desde el principio; los descriptores de bloque, desde el final—. Como `defrag()` mueve bloques, el usuario trabaja con un `Pointer` que vuelve a encontrar su bloque mediante un índice único. En 2026 los sanitizers y una revisión de código encontraron en él 13 errores, desde escrituras fuera del búfer hasta un puntero que apuntaba al bloque de otro; cada corrección tiene su prueba de regresión.

## Cómo funciona

- **Sin memoria adicional.** Los descriptores forman una lista doblemente enlazada ordenada por dirección, empaquetada al final del búfer sin huecos. La asignación busca el primer hueco que sirva (first fit) recorriendo la lista, O(número de bloques); liberar cuesta O(1).
- **Desfragmentación.** `defrag()` junta los bloques vivos en una sola pasada para que el espacio libre vuelva a ser una única región; `realloc()` amplía o reduce un bloque en su sitio cuando hay espacio.
- **Un puntero inteligente.** `Pointer` recuerda la posición del descriptor y el índice del bloque, y vuelve a encontrarlo después de que se mueve; un puntero a un bloque liberado devuelve `nullptr`.
- **Autocomprobaciones.** `check()` verifica todos los invariantes de la arena y `dump()` imprime su mapa.

## El precio, medido

El benchmark del README lo muestra sin rodeos: una asignación tarda 4,6 µs frente a 33 ns de `malloc`, porque recorre la lista; la compactación avanza a 6,4 GB/s de datos vivos, y desreferenciar un `Pointer` con la posición en caché cuesta 2,3 ns.

## Ingeniería

- Baterías de pruebas con GoogleTest sobre toda la API pública, una prueba de estrés aleatoria que compara byte a byte cada bloque vivo con un modelo y un objetivo de libFuzzer; las pruebas de estrés y el fuzzer llaman a `check()` después de cada operación.
- CI con GCC y Clang en Linux (también con AddressSanitizer y UndefinedBehaviorSanitizer), MSVC en Windows y Apple Clang en macOS, con las advertencias tratadas como errores; cada push en verde a `master` recibe una etiqueta de versión y una GitHub Release.
