#!/usr/bin/env python3
"""
app.py — Circuit Layout Optimization Platform v1.2
         Streamlit Web 界面

启动: streamlit run app.py
"""

import streamlit as st
import json
import tempfile
import os
import sys
import time
from pathlib import Path
from io import BytesIO

import pandas as pd

# Allow importing from src/
sys.path.insert(0, str(Path(__file__).parent))

from src.parser import parse_input
from src.layout import Layout, Module, Net
from src.cost import CostFunction
from src.optimizer import SimulatedAnnealing
from src.metrics import compute_metrics, print_metrics
from src.visualize import (
    draw_layout, draw_comparison, draw_cost_curve, draw_congestion_heatmap
)

# ── Page config ────────────────────────────────────────────────

st.set_page_config(
    page_title="Circuit Layout Optimization Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helpers ────────────────────────────────────────────────────

EXAMPLES = {
    "example_small.json (4 modules)": "data/example_small.json",
    "example_medium.json (10 modules)": "data/example_medium.json",
    "EDA Small (15 modules, macro+SC+IO)": "data/example_eda_small.json",
    "EDA Medium (24 modules, macro+SC+IO)": "data/example_eda_medium.json",
}


def build_layout(data: dict) -> Layout:
    modules = [
        Module(
            id=m["id"], width=m["width"], height=m["height"],
            x=m.get("x", 0.0), y=m.get("y", 0.0),
            module_type=m.get("type", "macro"),
            fixed=m.get("fixed", False),
        )
        for m in data["modules"]
    ]
    nets = [
        Net(
            name=n.get("name", f"net_{i}"),
            pins=n["pins"],
            weight=n.get("weight", 1.0),
        )
        for i, n in enumerate(data.get("nets", []))
    ]
    return Layout(
        chip_width=data["chip_width"],
        chip_height=data["chip_height"],
        modules=modules,
        nets=nets,
    )


@st.cache_data
def load_example_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def get_image_bytes(path: str) -> BytesIO | None:
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


# ── Title ──────────────────────────────────────────────────────

st.title("🧬 Circuit Layout Optimization Platform")
st.markdown("### 电路布局优化平台 — EDA / IC CAD Placement Optimization Demo")

# ── Sidebar ────────────────────────────────────────────────────

st.sidebar.header("⚙️ Input & Parameters")

# Input selection
st.sidebar.subheader("📂 Input Data")
example_choice = st.sidebar.selectbox(
    "Select built-in example",
    list(EXAMPLES.keys()),
    index=2,  # default to EDA small
)
uploaded_file = st.sidebar.file_uploader(
    "Or upload your own JSON file",
    type=["json"],
)

# Determine input path
if uploaded_file is not None:
    # Save uploaded file to temp
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, uploaded_file.name)
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    input_path = tmp_path
    input_label = f"Uploaded: {uploaded_file.name}"
else:
    input_path = EXAMPLES[example_choice]
    input_label = example_choice

# SA Parameters
st.sidebar.subheader("🔬 Simulated Annealing")
iterations = st.sidebar.slider("Iterations", 500, 10000, 2000, step=500)
init_temp = st.sidebar.slider("Initial Temperature", 100.0, 2000.0, 500.0, step=100.0)
cooling = st.sidebar.slider("Cooling Rate", 0.900, 0.999, 0.995, step=0.001)

# Cost Weights
st.sidebar.subheader("📐 Cost Function Weights")
alpha = st.sidebar.slider("α (HPWL)", 0.0, 10.0, 1.0, step=0.5)
beta = st.sidebar.slider("β (Overlap)", 0.0, 50.0, 10.0, step=1.0)
gamma = st.sidebar.slider("γ (Boundary)", 0.0, 500.0, 100.0, step=10.0)
delta = st.sidebar.slider("δ (Density)", 0.0, 20.0, 5.0, step=1.0)
epsilon = st.sidebar.slider("ε (Congestion)", 0.0, 10.0, 1.0, step=0.5)
use_hpwl = st.sidebar.checkbox("Use HPWL (EDA standard)", value=True)
grid_size = st.sidebar.slider("Congestion Grid Size", 5, 20, 10, step=1)

seed = st.sidebar.number_input("Random Seed", 0, 9999, 42)

# Run button
run_clicked = st.sidebar.button(
    "🚀 Run Optimization",
    type="primary",
    use_container_width=True,
)

# ── Main Area ──────────────────────────────────────────────────

# --- Project Intro (always visible) ---
with st.expander("📖 About This Platform", expanded=False):
    st.markdown("""
    This platform demonstrates **IC CAD Physical Design Placement Optimization**.

    **Features:**
    - Input circuit modules + netlist in JSON
    - Support **macro**, **standard cell**, **fixed IO** module types
    - **Simulated Annealing** optimization algorithm
    - Multi-objective cost function: **HPWL + Overlap + Boundary + Density + Congestion**
    - Full visualization: layout comparison, cost convergence, congestion heatmap

    **Corresponding EDA concepts:**
    Physical Design · Placement · Floorplanning · Wirelength Optimization · Congestion Estimation
    """)

# --- Input Data Preview ---
st.header("📂 Input Data Preview")

try:
    data = load_example_data(input_path)
except Exception as e:
    st.error(f"Failed to load input: {e}")
    st.stop()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Chip Size", f"{data['chip_width']}×{data['chip_height']}")
col2.metric("Modules", len(data["modules"]))
col3.metric("Nets", len(data["nets"]))
col4.metric("Macros", sum(1 for m in data["modules"] if m.get("type") == "macro"))
col5.metric("Std Cells", sum(1 for m in data["modules"] if m.get("type") == "standard_cell"))
col6.metric("Fixed", sum(1 for m in data["modules"] if m.get("fixed")))

tab1, tab2 = st.tabs(["📋 Modules", "🔗 Nets"])

with tab1:
    df_mod = pd.DataFrame([
        {
            "id": m["id"],
            "width": m["width"],
            "height": m["height"],
            "type": m.get("type", "macro"),
            "fixed": m.get("fixed", False),
            "x": m.get("x", "-"),
            "y": m.get("y", "-"),
        }
        for m in data["modules"]
    ])
    st.dataframe(df_mod, use_container_width=True, hide_index=True)

with tab2:
    # Normalize nets for display
    def net_summary(n):
        if "pins" in n:
            pins_str = " → ".join(n["pins"])
            return {
                "name": n.get("name", "-"),
                "pins": pins_str,
                "pin_count": len(n["pins"]),
                "weight": n.get("weight", 1.0),
            }
        return {
            "name": n.get("name", "-"),
            "pins": f"{n.get('source','?')} → {n.get('target','?')}",
            "pin_count": 2,
            "weight": n.get("weight", 1.0),
        }
    df_nets = pd.DataFrame([net_summary(n) for n in data["nets"]])
    st.dataframe(df_nets, use_container_width=True, hide_index=True)

# ── Optimization ───────────────────────────────────────────────

if not run_clicked:
    st.info("👈 Set parameters in the sidebar and click **Run Optimization** to start.")
    st.stop()

# --- Build layout & run optimization ---
with st.spinner("Running Simulated Annealing optimization..."):
    layout = build_layout(data)
    layout.randomize_positions(seed=seed)

    cost_fn = CostFunction(
        alpha=alpha, beta=beta, gamma=gamma,
        delta=delta, epsilon=epsilon,
        use_hpwl=use_hpwl,
    )

    # Initial metrics
    init_total, init_comp = cost_fn.total_cost(layout, grid_size)
    init_hpwl = cost_fn.hpwl(layout)
    init_cong = cost_fn.congestion_estimate(layout, grid_size)

    # Save initial layout
    draw_layout(layout, title="Initial Layout (Random)",
                output_path="outputs/initial_layout.png")

    # Run SA
    start_time = time.time()
    sa = SimulatedAnnealing(
        cost_fn=cost_fn,
        initial_temp=init_temp,
        cooling_rate=cooling,
        max_iter=iterations,
        grid_size=grid_size,
        seed=seed,
    )
    optimized = sa.optimize(layout, verbose=False)
    elapsed = time.time() - start_time

    # Final metrics
    opt_total, opt_comp = cost_fn.total_cost(optimized, grid_size)
    opt_hpwl = cost_fn.hpwl(optimized)
    opt_cong = cost_fn.congestion_estimate(optimized, grid_size)

    # Visualize
    draw_layout(optimized, title="Optimized Layout",
                output_path="outputs/optimized_layout.png")
    draw_comparison(layout, optimized, output_path="outputs/comparison.png")
    draw_cost_curve(sa.history, output_path="outputs/cost_curve.png")
    draw_congestion_heatmap(
        optimized, opt_cong["grid"], opt_cong["grid_size"],
        output_path="outputs/congestion_map.png",
    )

    # Save results
    hpwl_reduction = (1 - opt_hpwl / max(init_hpwl, 1e-6)) * 100
    cost_reduction = (1 - opt_total / max(init_total, 1e-6)) * 100

    result_data = optimized.to_result(
        cost=opt_total,
        wirelength=opt_comp[0],
        overlap=opt_comp[1],
        boundary=opt_comp[2],
        density=opt_comp[3],
        hpwl=opt_hpwl,
        max_congestion=opt_cong["max_congestion"],
        avg_congestion=opt_cong["avg_congestion"],
        congestion=opt_cong,
    )
    with open("outputs/result.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    summary = {
        "initial": {
            "hpwl": round(init_hpwl, 4),
            "total_cost": round(init_total, 4),
            "max_congestion": init_cong["max_congestion"],
            "avg_congestion": init_cong["avg_congestion"],
        },
        "optimized": {
            "hpwl": round(opt_hpwl, 4),
            "total_cost": round(opt_total, 4),
            "max_congestion": opt_cong["max_congestion"],
            "avg_congestion": opt_cong["avg_congestion"],
        },
        "hpwl_reduction_pct": round(hpwl_reduction, 2),
        "cost_reduction_pct": round(cost_reduction, 2),
        "elapsed_seconds": round(elapsed, 2),
        "iterations_completed": len(sa.history),
    }
    with open("outputs/metrics_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

# ── Results ────────────────────────────────────────────────────

st.success(f"✅ Optimization complete in {elapsed:.1f}s ({len(sa.history)} iterations)")

st.header("📊 Optimization Results")

# Metrics cards
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Initial HPWL", f"{init_hpwl:.1f}",
            delta=None, delta_color="off")
col2.metric("Optimized HPWL", f"{opt_hpwl:.1f}",
            delta=f"{hpwl_reduction:.1f}%", delta_color="inverse")
col3.metric("Initial Cost", f"{init_total:.1f}",
            delta=None, delta_color="off")
col4.metric("Optimized Cost", f"{opt_total:.1f}",
            delta=f"{cost_reduction:.1f}%", delta_color="inverse")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Congestion (Before)", f"{init_cong['max_congestion']}")
col2.metric("Congestion (After)", f"{opt_cong['max_congestion']}",
            delta=f"{opt_cong['max_congestion'] - init_cong['max_congestion']}",
            delta_color="inverse")
col3.metric("Overlap After", f"{opt_comp[1]:.1f}",
            delta="✅" if opt_comp[1] < 1e-6 else "⚠️")
col4.metric("Congested Cells", f"{opt_cong['congested_cells_count']}")

# ── Images ─────────────────────────────────────────────────────

st.header("🎨 Layout Visualization")

col1, col2 = st.columns(2)
with col1:
    if os.path.exists("outputs/initial_layout.png"):
        st.image("outputs/initial_layout.png",
                 caption="Initial Layout (Random)", use_container_width=True)
with col2:
    if os.path.exists("outputs/optimized_layout.png"):
        st.image("outputs/optimized_layout.png",
                 caption="Optimized Layout (SA)", use_container_width=True)

st.subheader("Side-by-Side Comparison")
if os.path.exists("outputs/comparison.png"):
    st.image("outputs/comparison.png",
             caption="Before vs After", use_container_width=True)

st.subheader("Convergence Analysis")
if os.path.exists("outputs/cost_curve.png"):
    st.image("outputs/cost_curve.png",
             caption="Cost Convergence Curves", use_container_width=True)

st.subheader("Congestion Heatmap")
if os.path.exists("outputs/congestion_map.png"):
    st.image("outputs/congestion_map.png",
             caption="Routing Congestion Map", use_container_width=True)

# ── Downloads ──────────────────────────────────────────────────

st.header("📥 Downloads")

col1, col2 = st.columns(2)
with col1:
    if os.path.exists("outputs/result.json"):
        with open("outputs/result.json", "rb") as f:
            st.download_button(
                "⬇ Download result.json",
                data=f.read(),
                file_name="result.json",
                mime="application/json",
                use_container_width=True,
            )
with col2:
    if os.path.exists("outputs/metrics_summary.json"):
        with open("outputs/metrics_summary.json", "rb") as f:
            st.download_button(
                "⬇ Download metrics_summary.json",
                data=f.read(),
                file_name="metrics_summary.json",
                mime="application/json",
                use_container_width=True,
            )

# ── JSON Preview ───────────────────────────────────────────────

with st.expander("📋 Result JSON Preview", expanded=False):
    if os.path.exists("outputs/result.json"):
        with open("outputs/result.json", "r") as f:
            st.json(json.load(f))

# ── Footer ─────────────────────────────────────────────────────

st.divider()
st.caption(
    "Circuit Layout Optimization Platform v1.2 · "
    "EDA / IC CAD Placement Demo · "
    "Built with Streamlit + Simulated Annealing"
)
