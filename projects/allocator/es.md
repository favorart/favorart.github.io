---
title: "allocator: un asignador de memoria con desfragmentación"
summary: "Un asignador de memoria en C++ sobre una arena fija capaz de desfragmentarse, acompañado de un puntero inteligente que sigue siendo válido cuando los bloques se mueven."
kind: Asignador de memoria · C++
---

Un proyecto de curso de 2015 en Technosphere, el programa de Mail.Ru Group y la Universidad Estatal de Moscú (MSU): un asignador de memoria que gestiona por sí mismo una arena fija en lugar de llamar al `malloc` del sistema.

## Cómo funciona

- **Sin memoria adicional.** El asignador entrega bloques de un búfer reservado de antemano, y su propia contabilidad —una lista doblemente enlazada de descriptores de bloque— vive en ese mismo búfer, empaquetada desde el final sin huecos. Asignar y liberar cuesta O(1).
- **Desfragmentación.** Tras muchas asignaciones y liberaciones, el espacio libre se fragmenta en trozos pequeños. El asignador junta los bloques vivos para que el espacio libre vuelva a ser una única región contigua; un bloque también puede reasignarse con un tamaño mayor.
- **Un puntero inteligente.** Mover bloques invalidaría los punteros crudos, así que el usuario trabaja a través de una clase `Pointer` que hace referencia a un descriptor de bloque y se actualiza cuando el bloque se mueve.
- **Pruebas.** El repositorio incluye un programa de pruebas para la asignación, la liberación, la reasignación y la desfragmentación.

## Por qué es importante

Los asignadores personalizados son una de las herramientas principales para optimizar el rendimiento en C++: menos llamadas al sistema, mejor localidad de los datos y un uso de memoria predecible. Este proyecto muestra la mecánica que hay debajo y el precio de mover objetos en memoria.
