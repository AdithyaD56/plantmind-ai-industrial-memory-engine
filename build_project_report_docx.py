from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "deliverables"
OUT_DIR.mkdir(exist_ok=True)
DOCX_PATH = OUT_DIR / "PlantMind_AI_Detailed_Report.docx"
ARCH_IMG = ROOT / "PlantMind_AI_Architecture.png"


def p(text: str) -> str:
    return escape(text).replace("\n", "<w:br/>")


def para(text: str, style: str | None = None, bold: bool = False, center: bool = False) -> str:
    align = '<w:jc w:val="center"/>' if center else ""
    pstyle = f'<w:pPr>{align}{f"<w:pStyle w:val=\"{style}\"/>" if style else ""}</w:pPr>'
    rpr = "<w:rPr><w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/><w:sz w:val=\"22\"/>" + ("<w:b/>" if bold else "") + "</w:rPr>"
    return f"<w:p>{pstyle}<w:r>{rpr}<w:t xml:space='preserve'>{p(text)}</w:t></w:r></w:p>"


def bullet(text: str, num_id: int = 1) -> str:
    return f"<w:p><w:pPr><w:pStyle w:val='ListBullet'/></w:pPr><w:r><w:rPr><w:rFonts w:ascii='Arial' w:hAnsi='Arial'/><w:sz w:val='22'/></w:rPr><w:t xml:space='preserve'>• {escape(text)}</w:t></w:r></w:p>"


def num(text: str) -> str:
    return f"<w:p><w:pPr><w:pStyle w:val='ListNumber'/></w:pPr><w:r><w:rPr><w:rFonts w:ascii='Arial' w:hAnsi='Arial'/><w:sz w:val='22'/></w:rPr><w:t xml:space='preserve'>{escape(text)}</w:t></w:r></w:p>"


content = []
content.append(para("PlantMind AI: Industrial Memory & Failure Prevention Engine", center=True, bold=True))
content.append(para("Detailed project document aligned with Problem Statement 8", center=True))
content.append(para("Team Members: Dhavala V D M Adithya Naidu | D Sai Karthik | K Harsha Vardhan Reddy", center=True))

def heading(text):
    content.append(f"<w:p><w:pPr><w:pStyle w:val='Heading1'/></w:pPr><w:r><w:rPr><w:rFonts w:ascii='Arial' w:hAnsi='Arial'/><w:sz w:val='28'/><w:b/></w:rPr><w:t xml:space='preserve'>{escape(text)}</w:t></w:r></w:p>")

def subheading(text):
    content.append(f"<w:p><w:pPr><w:pStyle w:val='Heading2'/></w:pPr><w:r><w:rPr><w:rFonts w:ascii='Arial' w:hAnsi='Arial'/><w:sz w:val='26'/><w:b/></w:rPr><w:t xml:space='preserve'>{escape(text)}</w:t></w:r></w:p>")

heading("1. Executive Summary")
content.append(para("PlantMind AI is an industrial knowledge intelligence platform designed to prevent failures before they happen. It ingests heterogeneous documents such as maintenance reports, incident logs, safety SOPs, inspection records, CSV files, and project documents, then transforms them into a continuously evolving industrial memory system."))
content.append(para("Unlike a normal document chatbot, the platform builds a knowledge graph, searches historical incidents, predicts failure risk, checks compliance, and gives cited answers to engineers. The result is an operational memory layer that helps industrial teams act early, reduce downtime, and retain lessons learned."))

heading("2. Problem Statement Alignment")
content.append(para("This project is aligned with Problem Statement 8 because it addresses the challenge of extracting industrial intelligence from disconnected operational documents and turning it into actionable, proactive failure prevention."))
for t in [
    "It learns from maintenance reports, incident reports, and safety documents instead of treating them as static files.",
    "It detects recurring failure patterns and surfaces risk before an unplanned shutdown occurs.",
    "It improves compliance awareness by comparing plant documents against safety and procedural requirements.",
    "It supports engineers with evidence-backed recommendations rather than generic chatbot replies.",
]:
    content.append(bullet(t))

heading("3. Project Objective")
content.append(para("The core objective of PlantMind AI is to create a living industrial memory that remembers every failure, every corrective action, and every relevant procedure."))
for t in [
    "Prevent repeat failures through historical pattern matching.",
    "Make industrial knowledge searchable, structured, and connected.",
    "Provide proactive alerts that help engineers inspect at-risk assets earlier.",
    "Deliver cited assistance for maintenance, compliance, and investigation workflows.",
]:
    content.append(bullet(t))

heading("4. System Overview")
content.append(para("The platform follows a pipeline architecture: Document Upload -> Document Intelligence -> Knowledge Graph Builder -> Failure Memory Engine -> Failure Intelligence Agent -> Compliance Agent -> Engineer Copilot."))
for t in [
    "Document Intelligence handles OCR, parsing, chunking, and structured extraction.",
    "The Knowledge Graph Builder links equipment, incidents, failures, procedures, locations, and personnel.",
    "The Failure Memory Engine stores and searches historical incidents for similarity.",
    "The Engineer Copilot answers questions using retrieved evidence and citations.",
]:
    content.append(bullet(t))

heading("5. Architecture Diagram")
content.append(para("The architecture diagram below shows the end-to-end PlantMind AI flow from industrial document ingestion to risk alerts and lessons learned."))
if ARCH_IMG.exists():
    content.append(f"<w:p><w:r><w:drawing><wp:inline xmlns:wp='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing' distT='0' distB='0' distL='0' distR='0'><wp:extent cx='6200000' cy='3500000'/><wp:docPr id='1' name='Architecture'/><a:graphic xmlns:a='http://schemas.openxmlformats.org/drawingml/2006/main'><a:graphicData uri='http://schemas.openxmlformats.org/drawingml/2006/picture'><pic:pic xmlns:pic='http://schemas.openxmlformats.org/drawingml/2006/picture'><pic:nvPicPr><pic:cNvPr id='0' name='Architecture.png'/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed='rId1' xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships'/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x='0' y='0'/><a:ext cx='6200000' cy='3500000'/></a:xfrm><a:prstGeom prst='rect'><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>")
content.append(para("The lower layer in the diagram shows the supporting stack: Streamlit for the interface, FastAPI for the backend, ChromaDB for semantic memory, NetworkX for the graph, SQLite for persistence, and OCR/document parsing for ingestion."))

heading("6. Detailed Functional Modules")
for head, items in [
    ("6.1 Document Intelligence Agent", [
        "Extracts text from PDFs and text-based files.",
        "Uses OCR for scanned or image-based documents.",
        "Parses CSV and Excel files into analyzable structures.",
        "Produces structured chunks and metadata for downstream intelligence.",
    ]),
    ("6.2 Knowledge Graph Builder", [
        "Identifies equipment IDs, locations, personnel, dates, procedures, and regulations.",
        "Connects equipment to failures and failure to root cause.",
        "Maps incident reports and SOPs into an industrial relationship graph.",
        "Creates a navigable memory structure using NetworkX.",
    ]),
    ("6.3 Failure Intelligence Agent", [
        "Compares new evidence with historical incidents.",
        "Computes failure similarity and risk score.",
        "Finds recurring root causes and similar equipment patterns.",
        "Generates recommended actions based on the inferred risk level.",
    ]),
    ("6.4 Compliance Agent", [
        "Checks uploaded documents against safety and SOP requirements.",
        "Highlights missing compliance elements.",
        "Generates compliance percentage and audit readiness score.",
        "Provides recommendations to close documentation gaps.",
    ]),
    ("6.5 Engineer Copilot", [
        "Answers questions about maintenance, failures, and compliance.",
        "Uses retrieval-based evidence from the document memory layer.",
        "Returns source citations so users can validate every answer.",
        "Supports investigation and decision-making rather than open-ended chat.",
    ]),
]:
    subheading(head)
    for item in items:
        content.append(bullet(item))

heading("7. Tech Stack")
table_rows = [
    ("Layer", "Technology Used"),
    ("Frontend", "Streamlit, Plotly, AgGrid"),
    ("Backend", "FastAPI"),
    ("AI / Workflow", "LangGraph, LangChain, Groq"),
    ("Vector Memory", "ChromaDB"),
    ("Knowledge Graph", "NetworkX"),
    ("Database", "SQLite"),
    ("OCR", "EasyOCR"),
    ("Document Parsing", "PyMuPDF, Unstructured"),
    ("ML", "Scikit-learn"),
]
table_xml = [
    "<w:tbl>",
    "<w:tblPr><w:tblW w:w='9360' w:type='dxa'/><w:tblBorders><w:top w:val='single' w:sz='6' w:color='D9E2F3'/><w:left w:val='single' w:sz='6' w:color='D9E2F3'/><w:bottom w:val='single' w:sz='6' w:color='D9E2F3'/><w:right w:val='single' w:sz='6' w:color='D9E2F3'/><w:insideH w:val='single' w:sz='6' w:color='D9E2F3'/><w:insideV w:val='single' w:sz='6' w:color='D9E2F3'/></w:tblBorders></w:tblPr>",
    "<w:tblGrid><w:gridCol w:w='2500'/><w:gridCol w:w='6860'/></w:tblGrid>",
]
for i, (a, b) in enumerate(table_rows):
    if i == 0:
        fill = "D9E2F3"
        bold = True
    else:
        fill = "FFFFFF"
        bold = False
    table_xml.append(
        f"<w:tr><w:tc><w:tcPr><w:tcW w:w='2500' w:type='dxa'/><w:shd w:fill='{fill}'/></w:tcPr>{para(a, bold=bold)}</w:tc><w:tc><w:tcPr><w:tcW w:w='6860' w:type='dxa'/><w:shd w:fill='{fill}'/></w:tcPr>{para(b, bold=bold)}</w:tc></w:tr>"
    )
table_xml.append("</w:tbl>")
content.append("".join(table_xml))

heading("8. Sample Demo Flow")
content.append(para("The prototype is designed for a live demonstration where a judge uploads industrial documents and immediately sees the memory engine in action."))
for t in [
    "Upload a maintenance report, an incident report, and a safety SOP.",
    "Show that OCR, extraction, and graph creation happen automatically.",
    "Open the Failure Intelligence view for equipment such as Pump P101.",
    "Ask the Engineer Copilot why the asset is at risk and show the citations.",
    "Finish by highlighting the proactive warning and recommended inspection window.",
]:
    content.append(num(t))

heading("9. Project Impact")
for t in [
    "Reduces repeated failures by learning from historical industrial events.",
    "Improves uptime by turning documents into actionable maintenance intelligence.",
    "Supports safer operations through compliance and procedure awareness.",
    "Preserves organizational memory even when staff and shift teams change.",
]:
    content.append(bullet(t))

heading("10. Conclusion")
content.append(para("PlantMind AI is built as an industrial operating system for knowledge. It combines document intelligence, knowledge graphs, failure memory, compliance checking, and an evidence-based copilot to help industries prevent failures before they happen."))
content.append(para("This makes the system highly aligned with Problem Statement 8 because it does not merely retrieve documents; it learns from them, connects them, and converts them into proactive operational intelligence."))

heading("Team Members")
for t in [
    "Dhavala V D M Adithya Naidu",
    "D Sai Karthik",
    "K Harsha Vardhan Reddy",
]:
    content.append(bullet(t))

document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
<w:body>
{''.join(content)}
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/><w:cols w:space="708"/><w:docGrid w:linePitch="360"/></w:sectPr>
</w:body>
</w:document>"""

content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""

rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/architecture.png"/>
</Relationships>"""

styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="Heading 1"/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="28"/><w:b/><w:color w:val="2E74B5"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="Heading 2"/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="26"/><w:b/><w:color w:val="1F4D78"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListNumber"><w:name w:val="List Number"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:style>
</w:styles>"""

numbering_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:abstractNum w:abstractNumId="1">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
  <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>"""

with ZipFile(DOCX_PATH, "w", ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types)
    z.writestr("_rels/.rels", rels)
    z.writestr("word/document.xml", document_xml)
    z.writestr("word/_rels/document.xml.rels", doc_rels)
    z.writestr("word/styles.xml", styles_xml)
    z.writestr("word/numbering.xml", numbering_xml)
    if ARCH_IMG.exists():
        z.write(ARCH_IMG, "word/media/architecture.png")

print(DOCX_PATH)

