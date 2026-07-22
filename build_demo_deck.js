const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

const ROOT = __dirname;
const OUT = path.join(ROOT, "deliverables");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const BG = "08111b";
const PANEL = "111c2b";
const BLUE = "2f6ea8";
const ORANGE = "ff8a00";
const WHITE = "f4f7fb";
const MUTED = "9bb0c7";
const GREEN = "67d18b";

function box(svg, x, y, w, h, text, fill, stroke) {
  const lines = text.split("\n");
  const fontSize = 22;
  const lineGap = 26;
  const total = lines.length * fontSize + (lines.length - 1) * 8;
  let html = `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="18" ry="18" fill="#${fill}" stroke="#${stroke}" stroke-width="4"/>`;
  let ty = y + h / 2 - total / 2 + fontSize;
  for (const line of lines) {
    html += `<text x="${x + w / 2}" y="${ty}" fill="#${WHITE}" font-size="${fontSize}" text-anchor="middle" font-family="Arial" font-weight="700">${escapeXml(line)}</text>`;
    ty += lineGap;
  }
  return svg + html;
}

function escapeXml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function architectureSvg(file) {
  let svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1100" viewBox="0 0 2200 1100">\n`;
  svg += `<rect width="2200" height="1100" fill="#${BG}"/>`;
  svg += `<text x="80" y="60" fill="#${ORANGE}" font-size="34" font-family="Arial" font-weight="700">PlantMind AI Architecture</text>`;
  svg += `<text x="80" y="100" fill="#${MUTED}" font-size="18" font-family="Arial">Document intake → knowledge graph → failure memory → risk alert → engineer copilot</text>`;
  svg = box(svg, 90, 180, 330, 120, "Industrial Documents\nPDF, CSV, SOP, Excel", PANEL, ORANGE);
  svg = box(svg, 500, 180, 340, 120, "Document Intelligence\nOCR + Parsing + Chunking", PANEL, BLUE);
  svg = box(svg, 915, 180, 325, 120, "Knowledge Graph Builder\nEquipment, incidents, failures", PANEL, BLUE);
  svg = box(svg, 1310, 180, 310, 120, "Failure Memory Engine\nSimilarity + history search", PANEL, GREEN);
  svg = box(svg, 1685, 180, 320, 120, "Risk Prediction Agent\nHigh / medium / low alert", PANEL, ORANGE);
  svg = box(svg, 180, 470, 355, 150, "ChromaDB + SQLite\nSemantic memory + records", PANEL, "5e7da0");
  svg = box(svg, 650, 470, 355, 150, "NetworkX Graph\nEquipment → failure → root cause", PANEL, "5e7da0");
  svg = box(svg, 1120, 470, 355, 150, "Compliance Agent\nFactory Act, OISD, SOP gaps", PANEL, "5e7da0");
  svg = box(svg, 1590, 470, 355, 150, "Engineer Copilot\nCited maintenance guidance", PANEL, "5e7da0");
  svg = box(svg, 120, 790, 580, 170, "Executive UI\nOverview • Graph • Failure Intelligence • Compliance • Copilot", PANEL, ORANGE);
  svg = box(svg, 760, 790, 620, 170, "Proactive Outcome\nWarn before failure, not after search", PANEL, GREEN);
  svg = box(svg, 1440, 790, 610, 170, "Deployment\nStreamlit + FastAPI + low-cost local stack", PANEL, BLUE);
  svg += `</svg>`;
  fs.writeFileSync(file, svg, "utf8");
}

function addTitle(slide, kicker, title, subtitle) {
  slide.addText(kicker.toUpperCase(), { x: 0.55, y: 0.3, w: 12, h: 0.25, fontSize: 12, bold: true, color: ORANGE, margin: 0 });
  slide.addText(title, { x: 0.55, y: 0.62, w: 12, h: 0.7, fontSize: 28, bold: true, color: WHITE, margin: 0 });
  if (subtitle) slide.addText(subtitle, { x: 0.55, y: 1.4, w: 12, h: 0.3, fontSize: 12, color: MUTED, margin: 0 });
}

function panel(slide, x, y, w, h, title, body, fill = PANEL, line = BLUE) {
  slide.addShape("roundRect", {
    x, y, w, h, fill: { color: fill }, line: { color: line, pt: 1.5 }, radius: 0.12, shadow: undefined,
  });
  slide.addText(title, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: 0.2, fontSize: 12, bold: true, color: ORANGE, margin: 0 });
  slide.addText(body, { x: x + 0.12, y: y + 0.3, w: w - 0.24, h: h - 0.36, fontSize: 10, color: WHITE, breakLine: false, margin: 0 });
}

function metric(slide, x, y, w, h, value, label) {
  slide.addShape("roundRect", {
    x, y, w, h, fill: { color: "0e1724" }, line: { color: "24405e", pt: 1.2 }, radius: 0.12,
  });
  slide.addText(value, { x, y: y + 0.12, w, h: 0.4, align: "center", fontSize: 22, bold: true, color: WHITE, margin: 0 });
  slide.addText(label, { x, y: y + 0.6, w, h: 0.18, align: "center", fontSize: 10, color: MUTED, margin: 0 });
}

function addConnector(slide, x1, y1, x2, y2) {
  slide.addShape("line", { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: "8ea8c7", pt: 1.6, beginArrowType: "none", endArrowType: "triangle" } });
}

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "PlantMind AI";
pptx.subject = "Industrial Memory and Failure Prevention Engine";
pptx.title = "PlantMind AI Presentation";
pptx.company = "PlantMind AI";
pptx.lang = "en-US";

const slidesDir = path.join(OUT, "slides");
if (!fs.existsSync(slidesDir)) fs.mkdirSync(slidesDir, { recursive: true });

const diagramPath = path.join(OUT, "PlantMind_AI_Architecture.svg");
architectureSvg(diagramPath);

let s = pptx.addSlide();
s.background = { color: BG };
addTitle(s, "Industrial Memory Engine", "PlantMind AI prevents failures before they happen.", "Working prototype for maintenance, safety, and compliance intelligence.");
panel(s, 0.6, 2.0, 5.9, 2.2, "What it does", "Ingests industrial documents, extracts equipment and failure signals, builds a knowledge graph, and returns proactive risk warnings with citations.");
panel(s, 6.8, 2.0, 5.9, 2.2, "Why it matters", "Plants lose time because lessons stay trapped in documents.\nPlantMind AI turns those documents into living memory that can warn engineers early.");
metric(s, 0.8, 4.6, 2.1, 1.15, "5", "AI Agents");
metric(s, 3.1, 4.6, 2.1, 1.15, "1", "Knowledge Graph");
metric(s, 5.4, 4.6, 2.1, 1.15, "48h", "Action window");
metric(s, 7.7, 4.6, 2.1, 1.15, "Cited", "Copilot answers");
metric(s, 10.0, 4.6, 2.1, 1.15, "Local", "Low-cost stack");

s = pptx.addSlide(); s.background = { color: BG };
addTitle(s, "Problem", "Industrial knowledge is fragmented, so repeat failures keep happening.");
panel(s, 0.7, 1.55, 3.8, 4.8, "Today’s reality", "Maintenance reports, SOPs, P&IDs, incident logs, and inspections live in separate files.\n\nEngineers spend time searching instead of preventing failures.\n\nCritical lessons are often forgotten once the incident closes.");
panel(s, 4.8, 1.55, 7.8, 4.8, "PlantMind AI answer", "A living industrial memory system that reads all plant documents, connects equipment to incidents and failure modes, and alerts the operator when a new report resembles a prior failure pattern.");

s = pptx.addSlide(); s.background = { color: BG };
addTitle(s, "Architecture", "The system flows from document ingestion to risk warning.");
s.addImage({ path: diagramPath, x: 0.45, y: 1.3, w: 12.4, h: 5.8 });

s = pptx.addSlide(); s.background = { color: BG };
addTitle(s, "How it works", "Each agent owns one industrial step.");
panel(s, 0.6, 1.5, 2.35, 3.0, "1. Document Intelligence", "Extract text from PDFs.\nOCR images.\nParse tables.\nChunk documents.\nProduce structured JSON.");
panel(s, 3.05, 1.5, 2.35, 3.0, "2. Graph Builder", "Extract equipment IDs.\nConnect incidents, root causes, procedures, and regulations.\nStore relationships in NetworkX.");
panel(s, 5.5, 1.5, 2.35, 3.0, "3. Failure Intelligence", "Compare current evidence with history.\nCompute similarity and risk.\nSuggest probable root causes.");
panel(s, 7.95, 1.5, 2.35, 3.0, "4. Compliance", "Check documents against SOP and safety requirements.\nReturn gaps and audit readiness.");
panel(s, 10.4, 1.5, 2.35, 3.0, "5. Copilot", "Answer questions with citations.\nGuide maintenance decisions.\nSupport failure investigations.");
panel(s, 1.1, 5.2, 11.1, 1.0, "Key innovation", "It remembers every failure and proactively warns the engineer when a new record looks like a repeat event.");

s = pptx.addSlide(); s.background = { color: BG };
addTitle(s, "Demo Flow", "Use the prototype to show a real industrial warning loop.");
panel(s, 0.7, 1.7, 2.4, 3.1, "Step 1", "Upload maintenance report\nUpload incident report\nUpload safety SOP");
panel(s, 3.4, 1.7, 2.4, 3.1, "Step 2", "Watch OCR and entity extraction\nSee graph creation\nObserve memory update");
panel(s, 6.1, 1.7, 2.4, 3.1, "Step 3", "Open Failure Intelligence\nShow similar incidents\nView risk score");
panel(s, 8.8, 1.7, 2.4, 3.1, "Step 4", "Ask the copilot\n'Why is Pump P101 at risk?'\nShow cited answer");
panel(s, 2.0, 5.2, 9.2, 0.95, "Judge message", "This is not a chatbot. It is an industrial operating system for knowledge, memory, and failure prevention.");

s = pptx.addSlide(); s.background = { color: BG };
addTitle(s, "Expected Deliverables", "Everything the hackathon asks for is covered.");
panel(s, 0.75, 1.55, 3.0, 4.6, "Working prototype", "FastAPI backend\nStreamlit dashboard\nKnowledge graph\nRisk prediction\nCopilot with citations");
panel(s, 4.15, 1.55, 3.0, 4.6, "Architecture diagram", "Standalone architecture visual\nAlso embedded in the deck\nShows the end-to-end industrial intelligence flow");
panel(s, 7.55, 1.55, 3.0, 4.6, "Presentation deck", "Clear narrative\nProblem → architecture → demo → impact\nBuilt for judges and live presentation");
panel(s, 10.95, 1.55, 1.6, 4.6, "Demo video", "Use the running prototype\nShow the sample plant memory\nAsk the copilot live");

pptx.writeFile({ fileName: path.join(OUT, "PlantMind_AI_Presentation.pptx") }).then(() => {
  console.log("Wrote:", path.join(OUT, "PlantMind_AI_Presentation.pptx"));
  console.log("Wrote:", diagramPath);
});
