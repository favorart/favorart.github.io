---
title: "Learning systems with discrete control"
summary: "Talk abstract: a system learns to position itself by trial and error, its experience is stored in a database, and a uniform grid of end positions combined with gradient descent yields accurate interpolation of controls."
source: sources.yml papers/lomonosov-2019-learning-systems
source_lang: ru
source_hash: 0502921f
translated: 2026-11-19
translator: Claude
reviewed: 2026-11-20
---
A system with discrete control learns to control itself by trial and error and by generalizing from them; the system's entire experience is stored in a database. The algorithm is tested in a virtual environment on a positioning task for two kinds of robots: a manipulator with 2–3 revolute and prismatic joints and a mobile robot with two tracks. A two-stage algorithm has been developed for constructing a uniform grid of end positions, which makes controls comparable and allows them to be averaged; it is shown that randomly generated controls without such a grid fail to produce good interpolation within a reasonable training time. Approaching target points along the grid is performed by stochastic gradient descent, and local interpolation of the control for nearby end positions ensures high positioning accuracy. To operate the trained system, the data are adapted on the fly: deviations observed when reference actions are repeated are recorded and clustered.
