"""PII Detection & Bias Guardrails — Three Tiers of PII Detection

This module demonstrates THREE approaches to PII handling, each a step up
in accuracy and production-readiness:

  1. NAIVE REGEX          — hand-rolled patterns (fast to prototype, misses
                            names, addresses, dates-of-birth, and many
                            locale-specific formats).

  2. PRESIDIO + spaCy     — Microsoft's open-source PII framework using
                            spaCy NER backend (50+ entity types, regex +
                            NLP hybrid, production-ready).

  3. PRESIDIO + TRANSFORMER MODEL — same Presidio pipeline, but the NER
                            backend is swapped to a HuggingFace transformer
                            fine-tuned for de-identification.  Higher
                            accuracy, especially for names, medical data,
                            and multilingual text.

     Popular PII / de-identification models:
       • dslim/bert-base-NER               — BERT-based general NER
       • obi/deid_roberta_i2b2             — RoBERTa fine-tuned on clinical text
       • StanfordAIMI/stanford-deidentifier-base — Stanford de-id model
       • urchade/gliner_multi_pii-v1        — GLiNER multilingual PII

In real applications, never ship approach #1 alone.  It exists here only so
students understand WHY a library like Presidio is necessary.

Install Presidio + spaCy (one-time):
    pip install presidio-analyzer presidio-anonymizer
    python -m spacy download en_core_web_lg

Install Presidio + Transformers (one-time):
    pip install "presidio-analyzer[transformers]" presidio-anonymizer
    python -m spacy download en_core_web_sm      # lightweight tokeniser
"""

import re
from utils.ollama_client import chat

# ── Try importing Presidio; fall back gracefully if not installed ──
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig

    _analyzer = AnalyzerEngine()          # default spaCy NER backend
    _anonymizer = AnonymizerEngine()
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

# ── Optional: transformer-backed Presidio engine ──
try:
    from presidio_analyzer.nlp_engine import TransformersNlpEngine

    # Uses a lightweight spaCy model for tokenisation only;
    # the heavy NER lifting is done by the BERT transformer model.
    _transformer_model_config = [
        {
            "lang_code": "en",
            "model_name": {
                "spacy": "en_core_web_sm",                  # tokeniser
                "transformers": "dslim/bert-base-NER",      # NER model
            },
        }
    ]
    _transformer_nlp_engine = TransformersNlpEngine(models=_transformer_model_config)
    _transformer_analyzer = AnalyzerEngine(nlp_engine=_transformer_nlp_engine)
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False


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
# APPROACH 3 — Presidio + Transformer NER model (highest accuracy)
# =====================================================================

def redact_transformer(text: str, language: str = "en") -> str:
    """Detect and anonymize PII using a HuggingFace transformer NER model.

    Instead of spaCy's statistical NER, this swaps in a BERT / RoBERTa
    model fine-tuned on NER or de-identification data.  The rest of
    Presidio's pipeline (regex recognizers, anonymizer operators) stays
    the same — only the NER backbone changes.

    Popular model choices (set in _transformer_model_config above):
      • dslim/bert-base-NER              — general-purpose NER
      • obi/deid_roberta_i2b2            — clinical de-identification
      • StanfordAIMI/stanford-deidentifier-base
    """
    if not PRESIDIO_AVAILABLE:
        print("[WARN] Presidio not installed — falling back to regex.")
        return redact_regex(text)
    if not TRANSFORMERS_AVAILABLE:
        print("[WARN] Transformers engine not available — falling back to spaCy Presidio.")
        return redact_presidio(text, language)

    results = _transformer_analyzer.analyze(text=text, language=language)

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
    """Best-available PII redaction: transformer > spaCy Presidio > regex."""
    if TRANSFORMERS_AVAILABLE:
        return redact_transformer(text)
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
    print("APPROACH 2 — Presidio + spaCy NER")
    print("=" * 60)
    print(redact_presidio(sample))

    print()
    print("=" * 60)
    print("APPROACH 3 — Presidio + Transformer NER model")
    print("=" * 60)
    print(redact_transformer(sample))

    # Show entity detection comparison
    if PRESIDIO_AVAILABLE:
        print()
        print("=" * 60)
        print("Entity detection — spaCy vs Transformer")
        print("=" * 60)

        spacy_results = _analyzer.analyze(text=sample, language="en")
        print("spaCy entities:")
        for r in spacy_results:
            print(f"  {r.entity_type:20s}  score={r.score:.2f}  '{sample[r.start:r.end]}'")

        if TRANSFORMERS_AVAILABLE:
            print()
            transformer_results = _transformer_analyzer.analyze(text=sample, language="en")
            print("Transformer (dslim/bert-base-NER) entities:")
            for r in transformer_results:
                print(f"  {r.entity_type:20s}  score={r.score:.2f}  '{sample[r.start:r.end]}'")
        else:
            print("\n  [Transformer engine not installed — see install instructions above]")

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
