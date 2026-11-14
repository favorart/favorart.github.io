---
title: "b-tree: un almacén clave-valor sobre un árbol B en C"
summary: "Un almacén clave-valor en disco escrito desde cero en C: un árbol B sobre páginas de tamaño fijo, claves y valores de cualquier longitud, una caché de páginas LRU y un registro de cambios (journal)."
kind: Motor de almacenamiento · C
---

Una pequeña base de datos embebida, escrita en 2015 para el curso de programación de sistemas de Technosphere, el programa de Mail.Ru Group y la Universidad Estatal de Moscú (MSU). La tarea consistía en construir desde cero la capa de almacenamiento que las bases de datos reales tienen por debajo: un almacén clave-valor con una interfaz al estilo de `dbopen` (`put`, `get`, `delete`, `sync`, `close`) que guarda sus datos en un único archivo.

## Cómo funciona

- **Árbol B sobre páginas.** El archivo se divide en páginas de tamaño fijo (4 KB por defecto); cada nodo del árbol es una página. Las claves y los valores pueden tener cualquier longitud.
- **Mapa de espacio libre.** Unas páginas de servicio guardan un mapa de bits de las páginas libres, de modo que las páginas eliminadas se reutilizan.
- **Caché LRU.** Las páginas usadas recientemente permanecen en memoria (16 MB por defecto); las páginas modificadas se escriben en disco al ser desalojadas.
- **Registro de cambios (journal).** Los cambios se escriben primero en el registro, para poder restaurar la base de datos tras una caída.
- **Configuración.** El tamaño del archivo, el de página y el de la caché se fijan al crear la base de datos.

## Por qué es importante

El proyecto aborda las cuestiones centrales de cualquier motor de almacenamiento: la disposición de las páginas, la división y fusión de nodos, la caché y la durabilidad. Es un camino directo del árbol B de los libros de texto a la forma en que están construidos SQLite o InnoDB.
