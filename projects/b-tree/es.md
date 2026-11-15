---
title: "b-tree: un almacén clave-valor sobre un árbol B en C"
summary: "Un almacén clave-valor en disco escrito desde cero en C: un árbol B sobre páginas de tamaño fijo, claves y valores de longitud variable, una caché de páginas LRU y un registro de escritura anticipada (journal) con recuperación tras caídas."
kind: Motor de almacenamiento · C
---

Una pequeña base de datos embebida, escrita en 2015 como proyecto de curso en Technosphere, el programa de Mail.Ru Group y la Universidad Estatal de Moscú (MSU). La tarea consistía en construir desde cero la capa de almacenamiento que las bases de datos reales tienen por debajo: un almacén clave-valor detrás de una API en C dada (`dbcreate`, `dbopen`, insertar, consultar, eliminar, sincronizar, cerrar) que guarda sus datos en un único archivo. En 2026 el proyecto volvió a la vida: se completaron la eliminación y la recuperación desde el registro, que estaban a medias, y todo quedó cubierto por pruebas.

## Cómo funciona

- **Árbol B sobre páginas.** El archivo se divide en páginas de tamaño fijo (4 KB por defecto); cada nodo del árbol es una página. Las claves y los valores de longitud variable se guardan directamente en los nodos, hasta 1/8 de página por entrada.
- **Divisiones y rebalanceo.** Las páginas llenas se dividen durante el descenso, en una sola pasada; las inserciones secuenciales dividen la página en el punto de inserción, así que las páginas quedan bien llenas. Al eliminar, una página con poco contenido se fusiona con su vecina o le toma entradas prestadas.
- **Mapa de espacio libre.** Unas páginas de servicio guardan un mapa de bits de las páginas libres, de modo que las páginas eliminadas se reutilizan.
- **Caché LRU.** Las páginas usadas recientemente permanecen en memoria (16 MB por defecto); las páginas modificadas se escriben en disco al ser desalojadas —todas a la vez, de modo que el archivo siempre contiene un árbol coherente—.
- **Registro de cambios (journal).** Cada cambio se escribe primero en un registro de escritura anticipada con sumas de verificación; al abrir la base, se vuelven a aplicar las entradas posteriores al último checkpoint, y una entrada cortada por una caída se descarta.
- **Configuración.** El tamaño del archivo, el de página y el de la caché se fijan al crear la base de datos.

## Ingeniería

- C99 y POSIX puros, sin dependencias, compilado con Make; Windows no es compatible.
- Pruebas con cmocka: pruebas unitarias de los módulos, operaciones aleatorias comparadas con un modelo de referencia, recuperación tras una caída en un proceso hijo y las cargas de peor caso; también se ejecutan con AddressSanitizer y UndefinedBehaviorSanitizer.
- CI en Linux (gcc y clang, con y sin los sanitizers) y macOS; el benchmark se ejecuta en cada push a `master`.
- Cada push a `master` que pasa la CI recibe una etiqueta de versión y una GitHub Release con la biblioteca para Linux y macOS.

## Por qué es importante

El proyecto aborda las cuestiones centrales de cualquier motor de almacenamiento: la disposición de las páginas, la división y fusión de nodos, la caché y la durabilidad. Es un camino directo del árbol B de los libros de texto a la forma en que están construidos SQLite o InnoDB.
