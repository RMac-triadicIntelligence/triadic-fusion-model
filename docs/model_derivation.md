# Mathematical Derivation of the Triadic Fusion Model

## Core Assumptions
- Subsystems are normalized to [0,1] maturity levels.
- Interactions are triadic: Each depends on the other two for growth.
- Dwelling acts as a hysteresis-like state, amplifying coupling in low-coherence regimes to model "trapped" innovation.
- Power scaling reflects physical constraints: Linear for baseline, nonlinear for synergies.

## Equations Derivation

### Coherence and Dwelling
Coherence \( c \) averages subsystem states. Dwelling \( d \) follows a logistic-like growth/decay:
\[
\frac{dd}{dt} = r_r (1-c)(1-d) - r_f c d
\]
This creates bistability: High d in low c, low d in high c.

### Coupling and Decay Modulation
Coupling \( k = 1 + b d \) boosts interactions during dwelling (e.g., crisis-driven collaboration).
Decay \( \delta = \delta_b (1 - \rho d) \) relieves loss in dwelling (e.g., sustained focus).

### Subsystem Dynamics
Using Hill functions for sigmoid activation (common in biological/chemical models):
\[
h(x) = \gamma \frac{x^s}{\theta^s + x^s}
\]
Growth term: Average activation from other subsystems, scaled by coupling and unused capacity (1-x).
Decay term: Proportional to current state, with subsystem-specific multipliers (e.g., x3 decays faster due to scaling challenges).

### Power Scaling
Base power: \( P_b = \rho_v V x_1 \), where \( \rho_v \) is volumetric density.
Synergy factor: Quadratic in \( x_2 x_3 \) to require high mutual maturity for exponential gains, mimicking threshold effects in fusion (e.g., Q>1 plasma).

## Stability Analysis
Fixed points: Solve \( \dot{x} = 0 \). Low-equilibrium (all ~0) stable without nudges; high-equilibrium (~1) via interventions. Dwelling introduces a saddle-node bifurcation.

## Extensions
- Add noise: Stochastic ODEs for realism.
- Optimize nudges: Use control theory to find optimal timing.
- Calibrate: Fit params to historical fusion data (e.g., ITER timelines).

This model is phenomenological; for physics-based fusion sims, integrate with tools like BOUT++ or GYRO.
