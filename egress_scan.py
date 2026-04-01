#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
import urllib.error

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.1:8b"

SYSTEM_PROMPT = """You are a security filter for outgoing AI-generated content.

Your job is to detect:
- API keys
- credentials
- PII (emails, phone numbers, addresses)
- sensitive business data
- anything that should not be shared externally

Return ONLY JSON:

{
  "classification": "SAFE" | "REDACT" | "BLOCK",
  "reason": "short reason",
  "redacted_text": "<text>"
}

Rules:
- BLOCK = highly sensitive (API keys, secrets)
- REDACT = partial sensitive info
- SAFE = no issues
- Keep reason short (<25 words)
- Always include redacted_text
"""

# Simple regex patterns
PATTERNS = {
    "api_key": r"(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z\-_]{35})",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
}

def regex_scan(text):
    findings = []
    redacted = text

    for name, pattern in PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings.append(name)
            redacted = re.sub(pattern, "[REDACTED]", redacted)

    return findings, redacted

def call_ollama(text):
    body = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    return json.loads(payload["message"]["content"])

def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()

    text = text.strip()

    if not text:
        print(json.dumps({
            "classification": "SAFE",
            "reason": "empty output",
            "redacted_text": text
        }))
        return

    findings, redacted = regex_scan(text)

    # If strong regex hit → BLOCK immediately
    if "api_key" in findings:
        print(json.dumps({
            "classification": "BLOCK",
            "reason": "API key detected",
            "redacted_text": "[BLOCKED]"
        }))
        return

    try:
        llama_result = call_ollama(redacted)
    except Exception:
        llama_result = {
            "classification": "REDACT" if findings else "SAFE",
            "reason": "fallback mode",
            "redacted_text": redacted
        }

    # Merge logic
    if findings and llama_result["classification"] == "SAFE":
        llama_result["classification"] = "REDACT"
        llama_result["reason"] = f"regex detected: {', '.join(findings)}"
        llama_result["redacted_text"] = redacted

    print(json.dumps(llama_result, ensure_ascii=False))

if __name__ == "__main__":
    main()
