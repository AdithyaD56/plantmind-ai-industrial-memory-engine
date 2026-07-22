from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
try:
    from st_aggrid import AgGrid, GridOptionsBuilder
except Exception:  # pragma: no cover - optional dependency
    AgGrid = None
    GridOptionsBuilder = None

from plantmind.core.config import CONFIG
from plantmind.services.industrial_service import IndustrialService
from plantmind.ui_utils import build_network_figure, industrial_theme, kpi_card, timeline_figure


st.set_page_config(page_title="PlantMind AI", page_icon="🏭", layout="wide")
st.markdown(industrial_theme(), unsafe_allow_html=True)


@st.cache_resource
def get_service() -> IndustrialService:
    return IndustrialService()


service = get_service()

with st.sidebar:
    st.markdown("## PlantMind AI")
    st.caption("Industrial Memory & Failure Prevention Engine")
    page = st.radio("Navigation", ["Executive Overview", "Knowledge Graph", "Failure Intelligence", "Compliance Center", "Engineer Copilot"])
    st.markdown("---")
    st.markdown("### Demo Inputs")
    upload = st.file_uploader("Upload industrial documents", type=["pdf", "txt", "csv", "json", "xlsx", "xls"])
    process_upload = st.button("Process Upload")
    if st.button("Load Sample Data"):
        from plantmind.tools.seed_demo import seed_demo_data

        seed_demo_data(service)
        st.success("Sample data loaded into memory.")


def render_hero():
    st.markdown(
        """
        <div class="pm-hero">
            <div class="pm-badge">Industrial OS</div>
            <div class="pm-badge">Failure Memory Engine</div>
            <div class="pm-badge">Graph Intelligence</div>
            <h1 style="margin-top:12px;margin-bottom:6px">PlantMind AI</h1>
            <p style="max-width:920px;color:#c5d6e8">
                A living industrial knowledge system that learns from maintenance reports, incidents, SOPs, and inspections to predict failures before they happen.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_upload(file_obj):
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_obj.name).suffix) as tmp:
        tmp.write(file_obj.read())
        tmp_path = Path(tmp.name)
    try:
        return service.ingest_file(tmp_path, file_obj.name, Path(file_obj.name).suffix.lstrip("."))
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def render_table(dataframe: pd.DataFrame, height: int = 250):
    if dataframe.empty:
        st.info("No records available yet.")
        return
    if AgGrid is None or GridOptionsBuilder is None:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
        return
    builder = GridOptionsBuilder.from_dataframe(dataframe)
    builder.configure_default_column(resizable=True, filter=True, sortable=True)
    builder.configure_pagination(paginationAutoPageSize=True)
    grid_options = builder.build()
    AgGrid(dataframe, gridOptions=grid_options, height=height, theme="streamlit")


def render_overview():
    data = service.overview()
    render_hero()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi_card("Documents Processed", data["documents_processed"]), unsafe_allow_html=True)
    c2.markdown(kpi_card("Equipment Tracked", data["equipment_tracked"]), unsafe_allow_html=True)
    c3.markdown(kpi_card("Incidents Identified", data["incidents_identified"]), unsafe_allow_html=True)
    c4.markdown(kpi_card("Risk Alerts", data["risk_alerts"]), unsafe_allow_html=True)
    c5.markdown(kpi_card("Compliance Score", f"{data['compliance_score']}%"), unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown("### Potential Failure Detected")
        if data["recent_incidents"]:
            incident = data["recent_incidents"][0]
            st.error(f"{incident['equipment_id']} | {incident['title']} | Root cause: {incident['root_cause']}")
            st.write("This evidence is being connected to the industrial memory graph and risk engine.")
        else:
            st.info("Upload a maintenance report or incident log to activate failure warnings.")

    with right:
        st.markdown("### Industrial Health")
        graph_summary = data["graph_summary"]
        st.metric("Graph Nodes", graph_summary.get("nodes", 0))
        st.metric("Graph Edges", graph_summary.get("edges", 0))
        st.metric("Node Types", len(graph_summary.get("node_types", {})))

    st.markdown("### Recent Documents")
    render_table(pd.DataFrame(data["recent_documents"]), height=260)
    st.markdown("### Recent Incidents")
    render_table(pd.DataFrame(data["recent_incidents"]), height=260)

    if data["recent_incidents"]:
        timeline_items = [
            {"date": row.get("incident_date"), "type": "Incident", "title": row.get("title"), "detail": row.get("root_cause")}
            for row in data["recent_incidents"][:12]
        ]
        st.markdown("### Industrial Timeline")
        st.plotly_chart(timeline_figure(timeline_items), use_container_width=True)


def render_graph():
    st.markdown("### Knowledge Graph Explorer")
    payload = service.graph_payload()
    node_types = sorted({node.get("type", "unknown") for node in payload.get("nodes", [])})
    selected_types = st.multiselect("Filter node types", node_types, default=node_types)
    search_term = st.text_input("Search label", value="")
    filtered_nodes = []
    allowed_ids = set()
    for node in payload.get("nodes", []):
        label = str(node.get("label", node.get("id", ""))).lower()
        if node.get("type", "unknown") in selected_types and (not search_term or search_term.lower() in label):
            filtered_nodes.append(node)
            allowed_ids.add(node["id"])
    filtered_edges = [edge for edge in payload.get("edges", []) if edge["source"] in allowed_ids and edge["target"] in allowed_ids]
    st.plotly_chart(build_network_figure({"nodes": filtered_nodes, "edges": filtered_edges, "summary": payload.get("summary", {})}), use_container_width=True)
    st.caption("Filter-ready knowledge graph linking equipment, incidents, failures, documents, and people.")


def render_failure():
    st.markdown("### Failure Intelligence")
    equipment = st.text_input("Equipment ID", value="P101")
    payload = service.failure_dashboard(equipment)
    insights = payload["insights"]
    if insights:
        insight = insights[0]
        cols = st.columns(4)
        cols[0].metric("Risk Score", insight["risk_score"])
        cols[1].metric("Similarity", insight["similarity_score"])
        cols[2].metric("Alert Level", insight["alert_level"])
        cols[3].metric("Similar Incidents", len(insight["similar_incidents"]))
        st.markdown("#### Risk Narrative")
        st.warning(
            f"High Risk Alert: {equipment} shows a pattern similar to previous failure events."
            if insight["risk_score"] >= 0.7
            else f"{equipment} requires monitoring and continued evidence gathering."
        )
        st.markdown("#### Root Cause Suggestions")
        st.write(insight["root_cause_suggestions"])
        st.markdown("#### Lessons Learned")
        st.write(insight["lessons_learned"])
        st.markdown("#### Recommended Actions")
        st.write(insight["recommended_actions"])
        st.markdown("#### Failure Clusters")
        render_table(pd.DataFrame(payload["clusters"]), height=260)


def render_compliance():
    st.markdown("### Compliance Center")
    result = service.compliance_dashboard()
    cols = st.columns(3)
    cols[0].metric("Compliance", f"{result['compliance_percent']}%")
    cols[1].metric("Audit Readiness", f"{result['audit_readiness_score']}%")
    cols[2].metric("Gaps", len(result["missing_requirements"]))
    st.markdown("#### Missing Requirements")
    render_table(pd.DataFrame({"missing_requirements": result["missing_requirements"]}), height=180)
    st.markdown("#### Recommendations")
    st.write(result["recommendations"])


def render_copilot():
    st.markdown("### Engineer Copilot")
    st.caption("Always cites source evidence.")
    question = st.text_area("Ask about equipment, maintenance, failures, or compliance", height=120, placeholder="Why is Pump P101 at risk?")
    if st.button("Ask PlantMind"):
        if question.strip():
            answer = service.ask(question)
            st.markdown("#### Answer")
            st.write(answer["answer"])
            st.markdown("#### Citations")
            render_table(pd.DataFrame(answer["citations"]), height=240)
            st.markdown("#### Follow-up Questions")
            st.write(answer["follow_up_questions"])
        else:
            st.warning("Please enter a question.")


if upload is not None and process_upload:
    result = handle_upload(upload)
    st.success(f"Ingested {result['document']['document_name']}")
    if result["failure_insights"]:
        st.warning("Potential failure intelligence has been updated.")


if page == "Executive Overview":
    render_overview()
elif page == "Knowledge Graph":
    render_graph()
elif page == "Failure Intelligence":
    render_failure()
elif page == "Compliance Center":
    render_compliance()
else:
    render_copilot()
