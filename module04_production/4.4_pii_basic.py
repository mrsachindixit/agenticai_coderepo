"""PII Detection — Naive Regex Approach (Baseline)

Hand-rolled regex patterns that catch obvious formats: email addresses,
phone numbers, credit-card numbers, and Social Security Numbers.

**Where this falls short:**
  • Misses person names, physical addresses, dates-of-birth, passport
    numbers, and every locale-specific format you didn't write a regex for.
  • No confidence scores — a match is all-or-nothing.
  • No entity typing beyond the four categories below.

This file exists so students can see *why* a library like Presidio or a
trained NER model is necessary.  Never ship regex-only PII detection
in a production system.

Progression:
  4.4  Regex baseline       ← you are here
  4.5  Presidio (spaCy + transformer NER models)
  4.6  LangChain PII middleware & reversible anonymiser
  4.7  Bias guardrails
"""

import re
from utils.ollama_client import chat

# ── Compiled patterns ──────────────────────────────────────────────

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
CREDIT_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


# ── Redaction ──────────────────────────────────────────────────────

def redact(text: str) -> str:
    """Replace PII-shaped substrings with bracketed placeholders."""
    text = EMAIL.sub("[EMAIL_REDACTED]", text)
    text = PHONE.sub("[PHONE_REDACTED]", text)
    text = CREDIT_CARD.sub("[CARD_REDACTED]", text)
    text = SSN.sub("[SSN_REDACTED]", text)
    return text


def scan_output_for_pii(llm_response: str) -> str:
    """Scan LLM output and redact any PII the model may have leaked."""
    return redact(llm_response)


# ── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = (
        "Email me at sachin@example.com and call +91 98765-43210. "
        "My SSN is 123-45-6789 and card 4111-1111-1111-1111. "
        "My name is Sachin Dixit and I live at 42 Elm Street."
    )

    print("=" * 60)
    print("Regex PII redaction")
    print("=" * 60)
    redacted = redact(sample)
    print(redacted)

    print()
    print("Limitations — these are NOT caught by regex:")
    print("  • Person name  : 'Sachin Dixit' — still visible above")
    print("  • Address       : '42 Elm Street' — still visible above")
    print("  • Date-of-birth, passport, IBAN, IP address, …")

    print()
    print("=" * 60)
    print("LLM call with regex PII guard on input + output")
    print("=" * 60)
    user_msg = "My email is sachin@example.com — summarise my account."
    safe_input = redact(user_msg)
    print(f"User (redacted): {safe_input}")

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Never reveal personal data."},
        {"role": "user", "content": safe_input},
    ]
    response = chat(messages, temperature=0.2)
    safe_output = scan_output_for_pii(response)
    print(f"LLM  (scanned) : {safe_output}")
