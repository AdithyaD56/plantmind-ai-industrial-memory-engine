from __future__ import annotations

import json
from typing import Any, Dict, List

import plotly.graph_objects as go
import networkx as nx


def industrial_theme() -> str:
    return """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(70,120,180,0.22), transparent 32%),
            radial-gradient(circle at bottom right, rgba(255,140,0,0.12), transparent 26%),
            linear-gradient(180deg, #09111c 0%, #0d1623 42%, #111a2a 100%);
        color: #f3f7fb;
    }
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #f3f7fb !important;
    }
    .pm-card {
        background: rgba(14, 23, 36, 0.88);
        border: 1px solid rgba(108, 146, 183, 0.22);
        border-radius: 18px;
        padding: 18px 18px 12px 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    }
    .pm-hero {
        background: linear-gradient(135deg, rgba(24,40,64,0.95), rgba(10,18,30,0.9));
        border: 1px solid rgba(255,140,0,0.22);
        border-radius: 22px;
        padding: 22px;
        margin-bottom: 18px;
    }
    .pm-badge {
        display:inline-block;
        background: rgba(255,140,0,0.16);
        border: 1px solid rgba(255,140,0,0.34);
        color: #ffb15e;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        letter-spacing: 0.02em;
        margin-right: 8px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #2e6ea6, #ff8c00);
        color: white;
        border: 0;
        border-radius: 12px;
        font-weight: 700;
    }
    .stDataFrame, .ag-theme-streamlit {
        border-radius: 16px;
        overflow: hidden;
    }
    </style>
    """


def kpi_card(label: str, value: Any, delta: str | None = None) -> str:
    delta_html = f"<div style='color:#ffb15e;font-size:12px;margin-top:6px'>{delta}</div>" if delta else ""
    return f"""
    <div class="pm-card">
      <div style="font-size:13px;color:#9fb4c9;text-transform:uppercase;letter-spacing:0.08em">{label}</div>
      <div style="font-size:30px;font-weight:800;margin-top:4px">{value}</div>
      {delta_html}
    </div>
    """


def build_network_figure(payload: Dict[str, Any]) -> go.Figure:
    graph = nx.MultiDiGraph()
    for node in payload.get("nodes", []):
        graph.add_node(node["id"], **node)
    for edge in payload.get("edges", []):
        graph.add_edge(edge["source"], edge["target"], **edge)

    pos = nx.spring_layout(graph.to_undirected(), seed=7, k=0.9) if graph.number_of_nodes() else {}
    type_colors = {
        "equipment": "#ff8c00",
        "incident": "#ff5f4d",
        "failure_mode": "#f5d547",
        "document": "#2e6ea6",
        "person": "#9fb4c9",
        "location": "#63b3ff",
        "chunk": "#7a8da3",
        "root_cause": "#ff7f50",
        "procedure": "#58d5ff",
        "regulation": "#7ee081",
    }
    fig = go.Figure()
    for source, target, edge_data in graph.edges(data=True):
        if source not in pos or target not in pos:
            continue
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color="rgba(140,170,200,0.22)", width=1.4),
                hoverinfo="none",
                showlegend=False,
            )
        )
    for node_id, node_data in graph.nodes(data=True):
        if node_id not in pos:
            continue
        x, y = pos[node_id]
        node_type = node_data.get("type", "unknown")
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(size=18 if node_type == "equipment" else 12, color=type_colors.get(node_type, "#9fb4c9"), line=dict(width=1, color="#ffffff")),
                text=[node_data.get("label", node_id)],
                textposition="top center",
                hovertemplate=f"{node_type}: %{{text}}<extra></extra>",
                showlegend=False,
            )
        )
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=680,
    )
    return fig


def timeline_figure(items: List[Dict[str, Any]]) -> go.Figure:
    fig = go.Figure()
    if not items:
        fig.update_layout(template="plotly_dark", height=360)
        return fig
    y_map = {"Incident": 3, "Inspection": 2, "Maintenance": 1, "Repair": 0}
    xs = list(range(len(items)))
    ys = [y_map.get(item.get("type"), 1.2) for item in items]
    colors = ["#ff8c00" if item.get("type") == "Incident" else "#2e6ea6" for item in items]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+lines", marker=dict(size=16, color=colors), line=dict(color="rgba(180,200,220,0.4)"), text=[f"{item.get('date','')}: {item.get('title','')}" for item in items], hovertemplate="%{text}<extra></extra>"))
    fig.update_layout(template="plotly_dark", height=360, yaxis=dict(visible=False), xaxis=dict(visible=False), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
