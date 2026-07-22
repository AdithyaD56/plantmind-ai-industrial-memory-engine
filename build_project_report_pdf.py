from pathlib import Path
from textwrap import wrap
import sys

DEPS = Path(__file__).resolve().parent / ".rl_deps"
if DEPS.exists():
    sys.path.insert(0, str(DEPS))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "deliverables"
OUT_DIR.mkdir(exist_ok=True)
PDF_PATH = OUT_DIR / "PlantMind_AI_Detailed_Report.pdf"
ARCH_IMG = ROOT / "PlantMind_AI_Architecture.png"


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitlePM", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, alignment=TA_CENTER, textColor=colors.HexColor("#1F3A5F"), spaceAfter=8))
styles.add(ParagraphStyle(name="SubPM", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=11, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceAfter=8))
styles.add(ParagraphStyle(name="MetaPM", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=10))
styles.add(ParagraphStyle(name="H1PM", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=colors.HexColor("#2E74B5"), spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="H2PM", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=colors.HexColor("#1F4D78"), spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyPM", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, leading=14, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallPM", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=11, textColor=colors.HexColor("#555555")))


def p(text, style="BodyPM"):
    return Paragraph(text, styles[style])


story = []
story.append(p("PlantMind AI: Industrial Memory & Failure Prevention Engine", "TitlePM"))
story.append(p("Detailed project document aligned with Problem Statement 8", "SubPM"))
story.append(p("Team Members: Dhavala V D M Adithya Naidu | D Sai Karthik | K Harsha Vardhan Reddy", "MetaPM"))

story.append(p("1. Executive Summary", "H1PM"))
story.append(p("PlantMind AI is an industrial knowledge intelligence platform designed to prevent failures before they happen. It ingests heterogeneous documents such as maintenance reports, incident logs, safety SOPs, inspection records, CSV files, and project documents, then transforms them into a continuously evolving industrial memory system."))
story.append(p("Unlike a normal document chatbot, the platform builds a knowledge graph, searches historical incidents, predicts failure risk, checks compliance, and gives cited answers to engineers. The result is an operational memory layer that helps industrial teams act early, reduce downtime, and retain lessons learned."))

story.append(p("2. Problem Statement Alignment", "H1PM"))
story.append(p("This project is aligned with Problem Statement 8 because it addresses the challenge of extracting industrial intelligence from disconnected operational documents and turning it into actionable, proactive failure prevention."))
for t in [
    "It learns from maintenance reports, incident reports, and safety documents instead of treating them as static files.",
    "It detects recurring failure patterns and surfaces risk before an unplanned shutdown occurs.",
    "It improves compliance awareness by comparing plant documents against safety and procedural requirements.",
    "It supports engineers with evidence-backed recommendations rather than generic chatbot replies.",
]:
    story.append(p(f"• {t}"))

story.append(p("3. Project Objective", "H1PM"))
story.append(p("The core objective of PlantMind AI is to create a living industrial memory that remembers every failure, every corrective action, and every relevant procedure."))
for t in [
    "Prevent repeat failures through historical pattern matching.",
    "Make industrial knowledge searchable, structured, and connected.",
    "Provide proactive alerts that help engineers inspect at-risk assets earlier.",
    "Deliver cited assistance for maintenance, compliance, and investigation workflows.",
]:
    story.append(p(f"• {t}"))

story.append(p("4. System Overview", "H1PM"))
story.append(p("The platform follows a pipeline architecture: Document Upload → Document Intelligence → Knowledge Graph Builder → Failure Memory Engine → Failure Intelligence Agent → Compliance Agent → Engineer Copilot."))
for t in [
    "Document Intelligence handles OCR, parsing, chunking, and structured extraction.",
    "The Knowledge Graph Builder links equipment, incidents, failures, procedures, locations, and personnel.",
    "The Failure Memory Engine stores and searches historical incidents for similarity.",
    "The Engineer Copilot answers questions using retrieved evidence and citations.",
]:
    story.append(p(f"• {t}"))

story.append(p("5. Architecture Diagram", "H1PM"))
story.append(p("The architecture diagram below shows the end-to-end PlantMind AI flow from industrial document ingestion to risk alerts and lessons learned."))
if ARCH_IMG.exists():
    story.append(Image(str(ARCH_IMG), width=6.8 * inch, height=3.8 * inch))
story.append(p("The lower layer in the diagram shows the supporting stack: Streamlit for the interface, FastAPI for the backend, ChromaDB for semantic memory, NetworkX for the graph, SQLite for persistence, and OCR/document parsing for ingestion."))

story.append(PageBreak())

story.append(p("6. Detailed Functional Modules", "H1PM"))
story.append(p("6.1 Document Intelligence Agent", "H2PM"))
for t in [
    "Extracts text from PDFs and text-based files.",
    "Uses OCR for scanned or image-based documents.",
    "Parses CSV and Excel files into analyzable structures.",
    "Produces structured chunks and metadata for downstream intelligence.",
]:
    story.append(p(f"• {t}"))

story.append(p("6.2 Knowledge Graph Builder", "H2PM"))
for t in [
    "Identifies equipment IDs, locations, personnel, dates, procedures, and regulations.",
    "Connects equipment to failures and failure to root cause.",
    "Maps incident reports and SOPs into an industrial relationship graph.",
    "Creates a navigable memory structure using NetworkX.",
]:
    story.append(p(f"• {t}"))

story.append(p("6.3 Failure Intelligence Agent", "H2PM"))
for t in [
    "Compares new evidence with historical incidents.",
    "Computes failure similarity and risk score.",
    "Finds recurring root causes and similar equipment patterns.",
    "Generates recommended actions based on the inferred risk level.",
]:
    story.append(p(f"• {t}"))

story.append(p("6.4 Compliance Agent", "H2PM"))
for t in [
    "Checks uploaded documents against safety and SOP requirements.",
    "Highlights missing compliance elements.",
    "Generates compliance percentage and audit readiness score.",
    "Provides recommendations to close documentation gaps.",
]:
    story.append(p(f"• {t}"))

story.append(p("6.5 Engineer Copilot", "H2PM"))
for t in [
    "Answers questions about maintenance, failures, and compliance.",
    "Uses retrieval-based evidence from the document memory layer.",
    "Returns source citations so users can validate every answer.",
    "Supports investigation and decision-making rather than open-ended chat.",
]:
    story.append(p(f"• {t}"))

story.append(p("7. Tech Stack", "H1PM"))
table_data = [
    ["Layer", "Technology Used"],
    ["Frontend", "Streamlit, Plotly, AgGrid"],
    ["Backend", "FastAPI"],
    ["AI / Workflow", "LangGraph, LangChain, Groq"],
    ["Vector Memory", "ChromaDB"],
    ["Knowledge Graph", "NetworkX"],
    ["Database", "SQLite"],
    ["OCR", "EasyOCR"],
    ["Document Parsing", "PyMuPDF, Unstructured"],
    ["ML", "Scikit-learn"],
]
tbl = Table(table_data, colWidths=[1.8 * inch, 4.7 * inch], repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("LEADING", (0, 0), (-1, -1), 11),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D3E0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(tbl)

story.append(p("8. Sample Demo Flow", "H1PM"))
story.append(p("The prototype is designed for a live demonstration where a judge uploads industrial documents and immediately sees the memory engine in action."))
for t in [
    "Upload a maintenance report, an incident report, and a safety SOP.",
    "Show that OCR, extraction, and graph creation happen automatically.",
    "Open the Failure Intelligence view for equipment such as Pump P101.",
    "Ask the Engineer Copilot why the asset is at risk and show the citations.",
    "Finish by highlighting the proactive warning and recommended inspection window.",
]:
    story.append(p(f"• {t}"))

story.append(p("9. Project Impact", "H1PM"))
for t in [
    "Reduces repeated failures by learning from historical industrial events.",
    "Improves uptime by turning documents into actionable maintenance intelligence.",
    "Supports safer operations through compliance and procedure awareness.",
    "Preserves organizational memory even when staff and shift teams change.",
]:
    story.append(p(f"• {t}"))

story.append(p("10. Conclusion", "H1PM"))
story.append(p("PlantMind AI is built as an industrial operating system for knowledge. It combines document intelligence, knowledge graphs, failure memory, compliance checking, and an evidence-based copilot to help industries prevent failures before they happen."))
story.append(p("This makes the system highly aligned with Problem Statement 8 because it does not merely retrieve documents; it learns from them, connects them, and converts them into proactive operational intelligence."))

story.append(p("Team Members", "H1PM"))
for t in [
    "Dhavala V D M Adithya Naidu",
    "D Sai Karthik",
    "K Harsha Vardhan Reddy",
]:
    story.append(p(f"• {t}"))

def add_page_num(canvas, doc):
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(7.7 * inch, 0.55 * inch, f"Page {canvas.getPageNumber()}")

doc = SimpleDocTemplate(
    str(PDF_PATH),
    pagesize=letter,
    rightMargin=1 * inch,
    leftMargin=1 * inch,
    topMargin=1 * inch,
    bottomMargin=1 * inch,
)
doc.build(story, onFirstPage=add_page_num, onLaterPages=add_page_num)
print(f"Wrote {PDF_PATH}")
