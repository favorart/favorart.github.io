---
tagline: "Biblioteca C++20 rápida y sin dependencias para VCD"
summary: "Una biblioteca en C++20 que escribe archivos de formas de onda VCD sin reservar memoria en cada cambio de valor y con una salida idéntica byte a byte en todos los sistemas operativos. Una auditoría con sanitizers encontró una corrupción del heap que 18 pruebas en verde no habían detectado."
kind: "Biblioteca · C++20"
---

Value Change Dump (VCD) es el formato de texto en el que los simuladores de hardware registran cómo cambian las señales a lo largo del tiempo; GTKWave y otros visores lo muestran como formas de onda. En 2017 porté a C++ la biblioteca de Python [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd). En 2026 la ejecuté con AddressSanitizer y UndefinedBehaviorSanitizer y encontré un desbordamiento de búfer en el heap, una desreferencia de puntero nulo, un destructor que lanzaba excepciones y una salida VCD no válida, todo oculto tras 18 pruebas que pasaban, porque el archivo de referencia con el que se comparaban había fijado la salida errónea. Tras las correcciones la biblioteca tiene 39 pruebas, y una reescritura de la ruta crítica hizo que `change()` fuera [entre 2 y 5 veces más rápido](https://github.com/favorart/vcd-writer/pull/10).

## Qué incluye

- **El estándar, punto por punto.** VCD de cuatro estados según IEEE 1364-2005 §18.2: cabecera, ámbitos anidados, los 18 tipos de variable, valores escalares, vectoriales y reales, `$dumpvars`, `$dumpoff` / `$dumpon`; los valores de cadena, como extensión de GTKWave. El README incluye una tabla con lo que está soportado y lo que no.
- **Sin reservas de memoria por cambio.** Los valores se formatean en un búfer de 64 KiB y se escriben con una sola llamada; el repositorio incluye un benchmark.
- **Validación sin efectos secundarios.** Los nombres, tamaños, valores y la fecha se comprueban antes de modificar cualquier estado, así que una llamada fallida no deja rastro en el archivo; una marca de tiempo en el pasado lanza una excepción.
- **Salida determinista tras una interfaz pequeña.** El archivo es idéntico byte a byte en todas las plataformas; el estado interno queda oculto tras pimpl y no hay dependencias de terceros.

## Ingeniería

- CI en Linux, Windows y macOS: GoogleTest y una comparación byte a byte con un archivo de referencia; un job aparte lo ejecuta todo con los sanitizers.
- Cada commit que pasa la CI recibe una etiqueta de versión semántica y una GitHub Release con bibliotecas precompiladas.
- Se integra en un proyecto CMake con `CPMAddPackage`; el README la compara, funcionalidad por funcionalidad, con pyvcd y cpp-vcd-tracer.
