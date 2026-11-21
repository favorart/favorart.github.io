---
title: "Learning algorithm of systems with discrete control"
summary: "Talk abstract: a model of a robot's pneumatic actuator as a random process, and an algorithm that compensates for the mechanism's drift on the fly and maintains positioning accuracy."
source: sources.yml papers/lomonosov-2020-learning-algorithm
source_lang: ru
source_hash: 5018b640
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---

Once installed at its workstation, a robot performs positioning movements continuously, while its mechanism and environment undergo changes over time that affect accuracy. We propose a model of the robot's muscle (pneumatic actuator) in the additive-multiplicative form of a random process: a deterministic component with velocity and acceleration constraints, high-frequency damped oscillations, low-frequency slow drift, and outliers. The learning algorithm filters out outliers, fits the non-stochastic parameters, and tracks the stochastic ones, switching on the fly between several operating scenarios of the muscle in order to maintain the required positioning accuracy. The robot is described as a non-homogeneous Markov decision process with discrete states and discrete time; learning uses a variant of hill climbing that moves to the first neighboring solution found to improve the result.
