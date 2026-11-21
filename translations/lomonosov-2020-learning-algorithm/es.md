---
title: "Algoritmo de aprendizaje de sistemas con control discreto"
summary: "Ponencia: modelo del accionamiento neumático de un robot como proceso aleatorio y un algoritmo que compensa sobre la marcha la deriva del mecanismo y mantiene la precisión de posicionamiento."
source: sources.yml papers/lomonosov-2020-learning-algorithm
source_lang: ru
source_hash: 5018b640
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---

Un robot, una vez instalado en su puesto de trabajo, realiza continuamente movimientos de posicionamiento, mientras que en su mecanismo y en el entorno se producen con el tiempo cambios que afectan a la precisión. Se propone un modelo del músculo (accionamiento neumático) del robot en forma aditivo-multiplicativa de proceso aleatorio: una componente determinista con restricciones de velocidad y aceleración, oscilaciones amortiguadas de alta frecuencia, una deriva lenta de baja frecuencia y valores atípicos. El algoritmo de aprendizaje filtra los valores atípicos, ajusta los parámetros no estocásticos y sigue la evolución de los estocásticos, alternando sobre la marcha entre varios escenarios de funcionamiento del músculo para mantener la precisión de posicionamiento requerida. El robot se describe mediante un proceso de decisión de Markov no homogéneo con estados discretos y tiempo discreto; para el aprendizaje se utiliza una variante del método de escalada (hill climbing) que pasa a la primera solución vecina encontrada que mejora el resultado.
