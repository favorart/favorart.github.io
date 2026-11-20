---
title: "Aprendizaje de sistemas con control discreto"
summary: "Ponencia: el sistema aprende a posicionarse por ensayo y error, la experiencia se almacena en una base de datos, y una malla uniforme de posiciones finales junto con el descenso de gradiente permite interpolar los controles con precisión."
source: sources.yml papers/lomonosov-2019-learning-systems
source_lang: ru
source_hash: 0502921f
translated: 2026-11-19
translator: Claude
reviewed: 2026-11-20
---
Un sistema con control discreto aprende a controlarse a sí mismo mediante ensayo y error y la generalización de sus resultados; toda la experiencia del sistema se almacena en una base de datos. El algoritmo se pone a punto en un entorno virtual con la tarea de posicionamiento de dos tipos de robots: un manipulador con 2–3 articulaciones rotacionales y prismáticas y un robot móvil con dos orugas. Se desarrolló un algoritmo de dos etapas para construir una malla uniforme de posiciones finales, que garantiza que los controles sean comparables y puedan promediarse; se muestra que, con controles generados aleatoriamente y sin dicha malla, no se logra una buena interpolación en un tiempo de aprendizaje razonable. La aproximación a los puntos objetivo sobre la malla se realiza mediante descenso de gradiente estocástico, y la interpolación local del control para las posiciones finales cercanas asegura una alta precisión al alcanzar el objetivo. Durante la operación del sistema ya entrenado, los datos se adaptan «sobre la marcha»: los desplazamientos que se producen al repetir las acciones de referencia se registran y se agrupan en clústeres.
