# Resume Project Description (English)

## One-Line Summary

Developed a circuit layout optimization prototype using Simulated Annealing for automated chip module placement with HPWL wirelength estimation, congestion analysis, and a Streamlit web visualization platform.

---

## 3 Resume Bullet Points

- Implemented **Simulated Annealing** in **Python** for multi-objective circuit placement optimization (HPWL wirelength, overlap, boundary, density, congestion), achieving 10-12% HPWL reduction on test cases
- Integrated **EDA-standard HPWL metric**, grid-based congestion estimation, and Macro/Standard Cell/Fixed IO constraints, bringing the prototype closer to real IC CAD placement scenarios
- Built an interactive **Streamlit** web platform with JSON upload, real-time parameter tuning, visualization of optimization results, and metric downloads

---

## 5 Detailed Bullet Points

1. Independently designed and implemented a **circuit layout optimization platform** covering the complete Placement flow in IC CAD Physical Design: JSON input parsing → data structure modeling → multi-objective cost function → Simulated Annealing optimization → visualization and analysis
2. Implemented a **five-dimensional cost function** centered on **HPWL (Half-Perimeter Wirelength)** — the EDA industry-standard wirelength metric — with independently tunable weights enabling trade-off analysis
3. Supported **Macro / Standard Cell / Fixed IO** module types and **multi-pin net** format, with fixed modules remaining stationary during optimization, reflecting real floorplanning constraints
4. Implemented grid-based **congestion estimation**, generating congestion heatmaps and incorporating congestion values into the cost function for routability-aware optimization
5. Built dual **CLI + Streamlit Web** interfaces; the web platform supports file upload, slider-based parameter tuning, real-time results visualization, and JSON result downloads suitable for technical demonstrations

---

## Tech Stack

Python · NumPy · Matplotlib · Streamlit · Simulated Annealing · HPWL · Congestion Estimation

---

## Keywords

IC CAD · EDA · Physical Design · Placement Optimization · HPWL · Macro Placement · Standard Cell · Fixed Constraints · Congestion Estimation · Simulated Annealing · Streamlit Web Platform · Multi-Objective Optimization
