---
title: "vcd-writer: una biblioteca en C++20 para archivos de formas de onda VCD"
summary: "Un port de pyvcd a C++20 sin dependencias que escribe archivos Value Change Dump (IEEE 1364-2005) sin reservar memoria en cada cambio de valor."
kind: Biblioteca · C++20
---

Value Change Dump (VCD) es el formato de texto en el que los simuladores de hardware registran cómo cambian las señales a lo largo del tiempo; visores como GTKWave lo muestran como formas de onda. **vcd-writer** genera esos archivos desde código C++: un simulador, un emulador o un banco de pruebas registra variables en ámbitos anidados y notifica sus cambios, y la biblioteca produce un archivo VCD que cualquier visor de formas de onda puede abrir.

Empezó en 2017 como un port de la biblioteca de Python [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd) y en 2026 se reescribió como una biblioteca moderna.

## Qué incluye

- **El estándar, verificado punto por punto.** VCD de cuatro estados según IEEE 1364-2005 §18.2: cabecera (`$date`, `$version`, `$timescale`, `$comment`), ámbitos anidados, los 18 tipos de variable, valores escalares, vectoriales, reales y de cadena, `$dumpvars`, `$dumpoff` / `$dumpon`. El README incluye una tabla con lo que está soportado y lo que no.
- **Sin reservas de memoria por cambio.** Los valores van a un búfer de salida de 64 KiB; el repositorio incluye un benchmark.
- **Validación sin efectos secundarios.** Los nombres, tamaños, valores y la fecha se comprueban antes de modificar cualquier estado, así que una llamada fallida no deja rastro en el archivo; una marca de tiempo en el pasado lanza una excepción.
- **Salida determinista.** El archivo es idéntico byte a byte en todas las plataformas.
- **Una interfaz limpia.** El estado interno queda oculto tras pimpl; no hay dependencias de terceros.

## Ingeniería

- CI en Linux, Windows y macOS con GoogleTest, AddressSanitizer y UndefinedBehaviorSanitizer.
- Cada commit que pasa la CI recibe una etiqueta de versión semántica y una GitHub Release con bibliotecas precompiladas.
- Se integra en un proyecto CMake con una sola llamada a `CPMAddPackage`.
- El README la compara, funcionalidad por funcionalidad, con pyvcd y cpp-vcd-tracer.

## Por qué es importante

Una biblioteca pequeña es un buen lugar para mostrar el ciclo de ingeniería completo: un estándar leído con atención, una API difícil de usar mal, un rendimiento medido y un proceso de publicación sin pasos manuales.
