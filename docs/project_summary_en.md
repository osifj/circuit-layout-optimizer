# Circuit Layout Optimization Platform — Project Summary

## Project Name

**Circuit Layout Optimization Platform**

A Placement Optimization prototype for IC CAD Physical Design

---

## Background

In the integrated circuit design flow, **Physical Design** is the critical stage that transforms a gate-level netlist into a physical chip layout. **Placement** — determining the 2D coordinates of circuit modules on the chip — is a core EDA problem that directly impacts chip area, timing, power, and manufacturability.

Industrial EDA tools (Synopsys IC Compiler, Cadence Innovus) and open-source alternatives (OpenROAD) invest significant engineering effort into solving the placement problem at scale.

This project was developed during an internship at **North IC Technology CAD** as a prototype platform to demonstrate understanding of placement optimization concepts, mathematical modeling, and algorithm implementation.

---

## Why Placement Optimization Matters in EDA

1. **Wirelength** directly affects signal delay and power consumption
2. **Module Overlap** is physically infeasible — two blocks cannot occupy the same silicon area
3. **Congestion** causes routing failures even when total wirelength is low
4. **Area Utilization** impacts chip cost — denser placement reduces die area
5. **Fixed Constraints** are ubiquitous in real designs (IO pads at chip edges, pre-placed SRAM macros)

These objectives are inherently conflicting, forming the core challenge of placement optimization.

---

## Project Goals

Build a prototype placement optimization system that:

1. Reads circuit modules, nets, and constraints (JSON)
2. Optimizes placement using **Simulated Annealing**
3. Uses **HPWL (Half-Perimeter Wirelength)** — the EDA industry standard metric
4. Implements a multi-objective cost function: wirelength + overlap + boundary + density + congestion
5. Supports **Macro / Standard Cell / Fixed IO** module types
6. Provides full visualization and evaluation metrics
7. Offers both **CLI** and **Streamlit Web** interfaces

---

## Key Technical Points

### HPWL (Half-Perimeter Wirelength)

```
HPWL_net = (max_x - min_x) + (max_y - min_y)
```

The bounding box half-perimeter of all pins in a net. More accurate than pairwise Manhattan distance, computationally efficient, and the de facto standard in placement research benchmarks (ISPD, ICCAD).

### Multi-Objective Cost Function

```
Total Cost = α × HPWL + β × Overlap + γ × Boundary + δ × Density + ε × Congestion
```

Five independently tunable dimensions for trade-off analysis.

### Module Types
- **Macro**: Large hard blocks (SRAM, CPU Core) — limited placement flexibility
- **Standard Cell**: Small logic gates — rendered smaller in visualization
- **Fixed IO**: Pre-placed modules — skipped during SA perturbation

### Congestion Estimation
Grid-based: G×G grid → L-shaped Manhattan route per net → per-cell net count → max/avg congestion → heatmap visualization

### Simulated Annealing
Classic stochastic global optimization. High temperature → exploration; low temperature → exploitation. Widely cited in placement literature.

---

## Experimental Results

| Test Case | Modules | HPWL Reduction | Cost Reduction | Congestion |
|-----------|---------|----------------|----------------|------------|
| EDA Small | 15 | -10.2% | -8.8% | 8→7 |
| EDA Medium | 24 | -12.0% | -11.6% | Cells 19→16 |

---

## Platform Features

- [x] JSON input (backward-compatible with source/target format)
- [x] Multi-pin net support
- [x] Macro / Standard Cell / Fixed IO module types
- [x] HPWL + pairwise wirelength
- [x] Overlap / Boundary / Density / Congestion penalties
- [x] Simulated Annealing (fixed module aware)
- [x] 6-panel convergence plots
- [x] Congestion heatmap
- [x] CLI with full parameter control
- [x] Streamlit Web platform (upload, tune, run, download)

---

## Current Limitations

1. Scale: SA convergence slows beyond ~100 modules
2. Simple routing model: L-shaped Manhattan vs. actual global router
3. No timing awareness
4. No row-based legalization for standard cells
5. JSON-only format (no DEF/LEF)
6. Single algorithm (SA only)

---

## Future Directions

- **Algorithm comparison**: Force-Directed, Genetic Algorithm
- **Larger benchmarks**: 50-100+ module test cases
- **Analytical placement + legalization**
- **DEF/LEF format support**
- **OpenROAD integration / comparison**
- **Reinforcement Learning / GNN-based placement**

---

## Keywords

IC CAD · EDA · Physical Design · Placement Optimization · HPWL · Macro Placement · Standard Cell · Fixed Constraints · Congestion Estimation · Simulated Annealing · Streamlit Web Platform
