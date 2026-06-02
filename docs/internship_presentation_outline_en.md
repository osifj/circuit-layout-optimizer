# Internship Presentation Outline (English)

**Presenter**: Chuanjie Wang  
**Project**: Circuit Layout Optimization Platform  
**Duration**: 8-10 minutes

---

## Slide 1 — Title

**Title**: Circuit Layout Optimization Platform — An EDA Placement Prototype

**Subtitle**: North IC Technology CAD Internship Project

**Content**: Name, internship unit, project name, date

---

## Slide 2 — Background: Placement in Chip Design

**What to say**:
> "In chip design, Physical Design is the stage where a gate-level netlist becomes a physical layout. Placement — assigning 2D coordinates to circuit modules — directly determines chip area, timing, power, and routability. The challenge is that these objectives conflict: shorter wires may cause overlaps, spreading modules apart increases wirelength."

**Visual**: IC design flow diagram, highlight Placement stage. Or project comparison image.

---

## Slide 3 — Problem Formulation

**Title**: Placement Optimization — Mathematical Model

**Content**:
```
Input:  Chip boundary (W,H) + N modules + K nets
Goal:   Find (x_i, y_i) for each module, minimizing:

Total Cost = α × HPWL     (wirelength)
           + β × Overlap   (module overlap)
           + γ × Boundary  (out-of-bounds)
           + δ × Density   (clustering)
           + ε × Congestion(routing hotspots)
```

**Visual**: Simple layout diagram with 3-4 rectangles and net connections

**What to say**:
> "I model placement as a multi-objective optimization problem with five cost components. Each has an independent weight for trade-off analysis."

---

## Slide 4 — System Architecture

**Title**: System Architecture

```
Input JSON → parser → layout → cost function
                                ↓
                      Simulated Annealing (SA)
                                ↓
                     visualize ← metrics ← result.json
```

| Module | Role |
|--------|------|
| parser.py | JSON parsing |
| layout.py | Data structures |
| cost.py | Multi-objective cost |
| optimizer.py | SA algorithm |
| visualize.py | Matplotlib plots |
| app.py | Streamlit Web UI |

**What to say**:
> "The system uses modular design. CLI and Web share the same backend — no code duplication."

---

## Slide 5 — HPWL & Multi-Objective Cost

**Title**: HPWL — The EDA Standard Metric

**HPWL**: `(max_x - min_x) + (max_y - min_y)` for each net's pin bounding box

| Method | 2-pin | Multi-pin | EDA Standard |
|--------|-------|-----------|-------------|
| Pairwise | O(pins²) | O(pins²) | ❌ |
| HPWL | O(pins) | O(pins) | ✅ |

**What to say**:
> "I use HPWL — the industry standard. For multi-pin nets, it computes the bounding box half-perimeter, which better approximates the actual Steiner tree routing."

---

## Slide 6 — Simulated Annealing

**Title**: Optimization Algorithm — Simulated Annealing

```
1. Random initial placement
2. T = T0
3. Loop:
   a. Pick movable module, perturb position
   b. Accept if ΔCost ≤ 0
      Otherwise accept with probability exp(-ΔCost/T)
   c. T = T × cooling_rate
4. Return best placement found
```

**Why SA**: No gradient needed, escapes local minima, classic placement baseline

**What to say**:
> "SA is a natural fit for placement — the cost function is non-differentiable, so gradient methods don't work. The probabilistic acceptance lets it escape local minima. It's widely used as a baseline in placement research."

---

## Slide 7 — EDA-Realistic Features

**Title**: Features Approaching Real EDA Scenarios

| Feature | Implementation |
|---------|---------------|
| Macro Placement | Large blocks, SA-placed |
| Standard Cells | Small cells, visually distinguished |
| Fixed IO Constraints | SA skips fixed modules |
| Multi-Pin Nets | HPWL bounding box |
| Congestion Estimation | G×G grid + heatmap |

**What to say**:
> "I added features that make the prototype closer to real EDA: fixed IO constraints, macro/SC distinction, multi-pin nets, and congestion estimation."

---

## Slide 8 — Web Platform Demo

**Title**: Streamlit Interactive Platform

**Live demo or screenshots**:
1. Select example → preview tables
2. Tune parameters (α/β/γ/δ/ε, iterations, temp)
3. Run → metrics update in real-time
4. 4 visualization types
5. Download result.json + metrics_summary.json

**What to say**:
> "I built a Streamlit web interface for easy demonstration. You can select data, tune parameters, and see results instantly."

---

## Slide 9 — Experimental Results

**Title**: Results

| Test | Modules | HPWL Reduction | Congestion |
|------|---------|----------------|------------|
| EDA Small | 15 | -10.2% | 8→7 |
| EDA Medium | 24 | -12.0% | Cells 19→16 |

**Visual**: Comparison image + cost curve + congestion heatmap

**What to say**:
> "Both test cases show 10-12% HPWL reduction with improved congestion distribution."

---

## Slide 10 — Summary & Future Work

**Done**:
- ✅ Complete placement optimization prototype
- ✅ HPWL + multi-objective cost
- ✅ Macro / SC / Fixed IO support
- ✅ Congestion estimation + heatmap
- ✅ CLI + Streamlit Web

**Limitations**: Scale, no timing, no DEF/LEF

**Future**:
- Algorithm comparison (Force-Directed, GA)
- Larger benchmarks
- Analytical placement + legalization
- OpenROAD integration
- RL-based placement

**What to say**:
> "This project demonstrates the complete placement optimization pipeline from modeling to implementation to platform deployment. The main limitation is scale — SA isn't suited for million-cell designs. Future work could explore analytical methods and OpenROAD integration."
