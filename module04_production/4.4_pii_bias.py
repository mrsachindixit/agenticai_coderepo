"""PII Detection & Bias Guardrails — Naive Regex vs Production-Grade Presidio

This module demonstrates TWO approaches to PII handling:

  1. NAIVE REGEX  — hand-rolled patterns (fast to prototype, misses edge cases)
  2. PRESIDIO     — Microsoft's open-source NLP-powered PII framework
                    (50+ entity types, pluggable recognizers, production-ready)

In real applications, never ship approach #1 alone.  It exists here only so
students understand WHY a library like Presidio is necessary.

Install Presidio (one-time):
    pip install presidio-analyzer presidio-anonymizer
    python -m spacy download en_core_web_lg
"""

import re
from utils.ollama_client import chat

# ── Try importing Presidio; fall back gracefully if not installed ──
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig

    _analyzer = AnalyzerEngine()
    _anonymizer = AnonymizerEngine()
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False


# =====================================================================
# APPROACH 1 — Naive regex (for comparison only)
# =====================================================================

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
CREDIT_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_regex(text: str) -> str:
    """Redact common PII patterns with regex.  NOT exhaustive — misses names,
    addresses, dates-of-birth, passport numbers, and many locale formats."""
    text = EMAIL.sub("[EMAIL_REDACTED]", text)
    text = PHONE.sub("[PHONE_REDACTED]", text)
    text = CREDIT_CARD.sub("[CARD_REDACTED]", text)
    text = SSN.sub("[SSN_REDACTED]", text)
    return text


# =====================================================================
# APPROACH 2 — Microsoft Presidio (production-grade)
# =====================================================================

def redact_presidio(text: str, language: str = "en") -> str:
    """Detect and anonymize PII using Presidio's NLP + regex hybrid engine.

    Presidio detects 50+ entity types out of the box:
    PERSON, EMAIL_ADDRESS, PHONE_NUMBER, CREDIT_CARD, US_SSN, LOCATION,
    DATE_TIME, IBAN_CODE, IP_ADDRESS, URL, and many more.

    Custom operators let you replace, mask, hash, or encrypt each type.
    """
    if not PRESIDIO_AVAILABLE:
        print("[WARN] Presidio not installed — falling back to regex-only redaction.")
        return redact_regex(text)

    results = _analyzer.analyze(text=text, language=language)

    # Custom operators: mask credit cards, replace everything else
    operators = {
        "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
        "PERSON": OperatorConfig("replace", {"new_value": "[NAME_REDACTED]"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL_REDACTED]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE_REDACTED]"}),
        "CREDIT_CARD": OperatorConfig("mask", {
            "masking_char": "*",
            "chars_to_mask": 12,
            "from_end": False,
        }),
    }

    anonymized = _anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators,
    )
    return anonymized.text


# =====================================================================
# Unified helpers — use Presidio when available, regex as fallback
# =====================================================================

def redact(text: str) -> str:
    """Best-available PII redaction: Presidio if installed, else regex."""
    return redact_presidio(text) if PRESIDIO_AVAILABLE else redact_regex(text)


def scan_output_for_pii(llm_response: str) -> str:
    """Scan LLM output and redact any PII the model may have leaked."""
    return redact(llm_response)


# =====================================================================
# Bias guardrails
# =====================================================================

SENSITIVE_GROUPS = ["race", "religion", "gender", "ethnicity", "nationality"]


def is_sensitive_comparison(text: str) -> bool:
    """Block comparative questions involving sensitive attributes."""
    lowered = text.lower()
    if any(g in lowered for g in SENSITIVE_GROUPS) and ("better" in lowered or "worse" in lowered):
        return True
    return False


BIAS_INSTRUCTIONS = (
    "Avoid stereotypes and be neutral. If a request seems biased, ask clarifying questions "
    "and avoid harmful generalizations. Never include personal data like email addresses, "
    "phone numbers, or credit card numbers in your responses."
)


# =====================================================================
# Demo
# =====================================================================

if __name__ == "__main__":
    sample = (
        "Email me at sachin@example.com and call +91 98765-43210. "
        "My SSN is 123-45-6789 and card 4111-1111-1111-1111. "
        "Does HR or Engineering earn more?"
    )

    print("=" * 60)
    print("APPROACH 1 — Naive regex redaction")
    print("=" * 60)
    print(redact_regex(sample))

    print()
    print("=" * 60)
    print("APPROACH 2 — Presidio (NLP + regex hybrid)")
    print("=" * 60)
    print(redact_presidio(sample))

    if PRESIDIO_AVAILABLE:
        # Show what Presidio detected (entity types + positions)
        print()
        print("Presidio detected entities:")
        for r in _analyzer.analyze(text=sample, language="en"):
            print(f"  {r.entity_type:20s}  score={r.score:.2f}  '{sample[r.start:r.end]}'")

    print()
    print("=" * 60)
    print("Bias guard + LLM call")
    print("=" * 60)
    user = "Does HR or Engineering earn more?"
    if is_sensitive_comparison(user):
        print("I can help with general info, but I can't compare groups in a sensitive way.")
    else:
        safe = redact(user)
        messages = [
            {"role": "system", "content": BIAS_INSTRUCTIONS},
            {"role": "user", "content": safe},
        ]
        response = chat(messages, temperature=0.2)
        safe_response = scan_output_for_pii(response)
        print(safe_response)
