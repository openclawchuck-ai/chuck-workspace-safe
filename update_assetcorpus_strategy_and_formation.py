#!/usr/bin/env python3
"""Apply October 6 founder positioning and formation-timing decisions to DOCX files."""

from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def text(p):
    return "".join((n.text or "") for n in p.iter(W + "t"))


def set_text(p, value):
    nodes = list(p.iter(W + "t"))
    if not nodes:
        run = ET.SubElement(p, W + "r")
        nodes = [ET.SubElement(run, W + "t")]
    nodes[0].text = value
    for node in nodes[1:]:
        node.text = ""


def rewrite(source, destination, transform):
    with ZipFile(source, "r") as zin:
        root = ET.fromstring(zin.read("word/document.xml"))
        transform(root)
        updated = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with ZipFile(destination, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                payload = updated if item.filename == "word/document.xml" else zin.read(item.filename)
                zout.writestr(item, payload)


def replace_paragraphs(root, replacements):
    found = set()
    for p in root.iter(W + "p"):
        current = text(p).strip()
        if current in replacements:
            set_text(p, replacements[current])
            found.add(current)
    missing = set(replacements) - found
    if missing:
        raise RuntimeError(f"Missing paragraph anchors: {sorted(missing)}")


def update_roadmap(root):
    replacements = {
        "Stage 1 — Package the thesis (Days 1–7)": "Stage 1 — Refresh the thesis and buyer-discovery package (Days 1–7)",
        "Publish the polished Word business plan. -Chuck, is this done yet? Comment back to me with a link to review": (
            "Refresh and publish the AssetCorpus business plan around the U.S.-based data-commercialization mission, the broad-company/narrow-beachhead strategy, and the discover–qualify–enhance–package–match–transact workflow."
        ),
        "Complete the 90-day interview and diligence toolkit. -Chuck, is this done yet?  Comment back to me with a link to review": (
            "Refresh the 90-day validation playbook, buyer interview guide, seller-intake and rights questions, dataset passport, evidence log, and decision scorecard."
        ),
        "Build a source-backed competitor database and prioritized target lists. -Chuck, is this done yet?": (
            "Update the source-backed competitor map and prepare the first 10 qualified U.S. buyer targets, with corrosion/NDT as the initial proof cohort."
        ),
        "Decide whether industrial maintenance/inspection remains the first vertical after 5–8 expert conversations.": (
            "Use corrosion/NDT as the initial validation beachhead for 5–8 expert/buyer conversations, while positioning AssetCorpus as a broader U.S.-based marketplace and data-commercialization network."
        ),
        "Decision gate: a narrow buyer problem, dataset type, and initial geography are specific enough to recruit both sides.": (
            "Decision gate: Tony approves the refreshed business plan, first 10 targets, outreach language, and interview package; 5–8 conversations then confirm whether one corrosion/NDT buyer problem and dataset type are specific enough to recruit both sides."
        ),
    }
    replace_paragraphs(root, replacements)

    body = root.find(".//" + W + "body")
    initial = next(p for p in body.iter(W + "p") if text(p).strip().startswith("Initial geography —"))
    children = list(body)
    container = next(node for node in children if initial is node or initial in list(node.iter(W + "p")))
    idx = children.index(container) + 1
    for value in [
        "Mission — AssetCorpus unlocks valuable data trapped on organizational hard drives, improves it into trusted and usable AI assets, and connects it with serious U.S. buyers who will pay for quality, provenance, and access.",
        "Scope — AssetCorpus is a broad U.S.-based data-commercialization marketplace. Corrosion/NDT is the initial validation beachhead, not the permanent company boundary.",
    ]:
        p = deepcopy(initial)
        set_text(p, value)
        body.insert(idx, p)
        idx += 1


def update_formation(root):
    body = root.find(".//" + W + "body")
    gate1 = next(p for p in body.iter(W + "p") if text(p).strip() == "Gate 1 — choose formation state")
    children = list(body)
    container = next(node for node in children if gate1 is node or gate1 in list(node.iter(W + "p")))
    idx = children.index(container)
    immediate = next(p for p in body.iter(W + "p") if text(p).strip().startswith("Immediate decision —"))
    records = [
        (gate1, "Formation timing recommendation — validate first; form before commercial exposure"),
        (immediate, "An LLC is not required for internal planning, market research, target-list development, or nonbinding customer-discovery conversations conducted transparently as a pre-formation venture."),
        (immediate, "Formation trigger — complete entity formation before AssetCorpus signs a contract or NDA in its own name, accepts payment, opens a business bank account, receives or controls nonpublic dataset samples, hires or pays contractors, incurs material liability, or represents itself as an existing LLC."),
        (immediate, "Near-term sequence — complete the Stage 1 package, obtain Tony’s outreach approval, and conduct 5–8 discovery conversations. Revisit the Florida LLC decision at that evidence checkpoint or sooner if a counterparty requests an entity, NDA, sample exchange, pilot, or commercial proposal."),
        (immediate, "Boundary — This is an operating recommendation, not legal or tax advice. Tony separately approves formation, filing facts, vendors, fees, contracts, outreach, and spending after appropriate professional review."),
    ]
    for template, value in records:
        p = deepcopy(template)
        set_text(p, value)
        body.insert(idx, p)
        idx += 1


def main():
    base = Path("/home/chuck/.openclaw/work-docs/assetcorpus-post-feedback")
    rewrite(base / "roadmap.source.docx", base / "roadmap.updated.docx", update_roadmap)
    rewrite(base / "formation.source.docx", base / "formation.updated.docx", update_formation)


if __name__ == "__main__":
    main()
