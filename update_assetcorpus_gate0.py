#!/usr/bin/env python3
"""Apply the approved AssetCorpus Gate 0 record to two DOCX files."""

from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraph_text(p):
    return "".join((node.text or "") for node in p.iter(W + "t"))


def set_paragraph_text(p, text):
    text_nodes = list(p.iter(W + "t"))
    if text_nodes:
        text_nodes[0].text = text
        for node in text_nodes[1:]:
            node.text = ""
        return
    run = ET.SubElement(p, W + "r")
    node = ET.SubElement(run, W + "t")
    node.text = text


def rewrite_docx(source, destination, transform):
    with ZipFile(source, "r") as zin:
        xml = zin.read("word/document.xml")
        root = ET.fromstring(xml)
        transform(root)
        updated = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with ZipFile(destination, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = updated if item.filename == "word/document.xml" else zin.read(item.filename)
                zout.writestr(item, data)


def update_roadmap(root):
    replacements = {
        "Gate 0 — Strategy alignment (Tony)": "Gate 0 — Strategy alignment (Tony) — COMPLETE 6 OCTOBER 2026",
        "Confirm four inputs before investor materials or development scope:": "Approved Gate 0 decision record:",
        "Funding path: bootstrap, outside investment, or undecided. -Chuck, I’ll fund with my own capital. $5K start up proof of concept limit.": (
            "Funding path: Bootstrap and self-fund the proof of concept, subject to a hard $5,000 ceiling. "
            "Every expense requires Tony’s itemized approval; the ceiling is not a spending authorization."
        ),
        "Existing relationships in data-rich industries. - Chuck, I have none.": (
            "Existing relationships: None in data-rich industries. Validation will begin with a U.S.-only cold-start discovery pipeline."
        ),
        "Near-term objective: personally validate, recruit a founding team, or prepare to raise. - Chuck, personally validate.": (
            "Near-term objective: Tony will personally validate demand and supply before recruiting a founding team or seeking outside capital."
        ),
        "Initial geography.": (
            "Initial geography: United States first. Commercial validation is nationwide, with early corrosion/NDT outreach concentrated in Gulf Coast-heavy markets where useful. "
            "This does not change the separate Florida formation-jurisdiction analysis."
        ),
    }
    seen = set()
    for p in root.iter(W + "p"):
        current = paragraph_text(p).strip()
        if current in replacements:
            set_paragraph_text(p, replacements[current])
            seen.add(current)
    missing = set(replacements) - seen
    if missing:
        raise RuntimeError(f"Roadmap anchors not found: {sorted(missing)}")


def update_formation(root):
    body = root.find(".//" + W + "body")
    paragraphs = [node for node in list(body) if node.tag == W + "p"]
    immediate_container = next(
        node for node in list(body)
        if paragraph_text(node).startswith("Immediate decision —")
    )
    immediate = next(immediate_container.iter(W + "p"))
    gate1 = next(p for p in paragraphs if paragraph_text(p).strip() == "Gate 1 — choose formation state")

    records = [
        (gate1, "Gate 0 — strategy alignment — COMPLETE 6 OCTOBER 2026"),
        (immediate, "Funding: Bootstrap/self-funded proof of concept with a hard $5,000 ceiling. Each expense requires Tony’s itemized approval; this record authorizes no spending."),
        (immediate, "Relationships: No existing relationships in data-rich industries. Customer discovery will use a U.S.-only cold-start pipeline; no outreach is authorized by this decision record."),
        (immediate, "Near-term objective: Tony will personally validate the opportunity before recruiting a founding team or raising outside capital."),
        (immediate, "Commercial-validation geography: United States first, with initial corrosion/NDT targeting concentrated in Gulf Coast-heavy markets where useful and qualified prospects considered nationwide."),
        (immediate, "Formation distinction: U.S.-first describes the market-validation scope. It does not replace the separate formation-state decision or authorize a filing. Florida remains subject to Tony’s formation approval and appropriate legal/tax review."),
    ]

    insertion_index = list(body).index(immediate_container) + 1
    for template, text in records:
        node = deepcopy(template)
        set_paragraph_text(node, text)
        body.insert(insertion_index, node)
        insertion_index += 1


def main():
    base = Path("/home/chuck/.openclaw/work-docs/assetcorpus-gate0")
    roadmap_out = base / "05-validation-roadmap-gate0-2026-10-06.docx"
    formation_out = base / "ai-data-marketplace-formation-action-plan-gate0-2026-10-06.docx"
    rewrite_docx(base / "05-validation-roadmap.source.docx", roadmap_out, update_roadmap)
    rewrite_docx(base / "formation-action-plan.source.docx", formation_out, update_formation)
    print(roadmap_out)
    print(formation_out)


if __name__ == "__main__":
    main()
