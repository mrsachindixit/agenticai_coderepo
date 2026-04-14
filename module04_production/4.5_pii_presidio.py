"""PII Detection — Microsoft Presidio (Production-Grade)

Presidio is Microsoft's open-source PII framework.  It combines **rule-based
recognisers** (regex, deny-lists, checksums) with **NLP-based NER** to detect
50+ entity types out of the box: PERSON, EMAIL_ADDRESS, PHONE_NUMBER,
CREDIT_CARD, US_SSN, LOCATION, DATE_TIME, IBAN_CODE, IP_ADDRESS, URL, …

This file demonstrates TWO NER backends that Presidio supports:

  • **spaCy** (default)         — `en_core_web_lg` statistical NER model
  • **HuggingFace Transformer** — e.g. `dslim/bert-base-NER`, a BERT model
    fine-tuned on NER data.  Higher accuracy, especially for names, medical
    records, and multi-lingual text.

Both use the same Presidio `AnalyzerEngine` → `AnonymizerEngine` pipeline;
only the NER backbone changes.

Popular PII / de-identification transformer models:
  • dslim/bert-base-NER                    — BERT general-purpose NER
  • obi/deid_roberta_i2b2                  — RoBERTa clinical de-id
  • StanfordAIMI/stanford-deidentifier-base — Stanford de-id
  • urchade/gliner_multi_pii-v1            — GLiNER multilingual PII

Install (one-time):
    pip install presidio-analyzer presidio-anonymizer
    python -m spacy download en_core_web_lg          # spaCy backend

    # Optional: transformer backend (bigger download)
    pip install "presidio-analyzer[transformers]"
    python -m spacy download en_core_web_sm           # lightweight tokeniser

Progression:
  4.4  Regex baseline
  4.5  Presidio (spaCy + transformer NER models) ← you are here
  4.6  LangChain PII middleware & reversible anonymiser
  4.7  Bias guardrails
"""

from utils.ollama_client import chat

# ── Import Presidio; fail-fast with a helpful message ──────────────
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
except ImportError as exc:
    raise SystemExit(
        "Presidio is not installed.  Run:\n"
        "  pip install presidio-analyzer presidio-anonymizer\n"
        "  python -m spacy download en_core_web_lg"
    ) from exc


# =====================================================================
# APPROACH 1 — Presidio + spaCy NER (default)
# =====================================================================

_spacy_analyzer = AnalyzerEngine()        # uses spaCy NER by default
_anonymizer = AnonymizerEngine()

# Shared anonymisation operators — same for every backend
OPERATORS = {
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


def redact_spacy(text: str, language: str = "en") -> str:
    """Detect and anonymise PII using Presidio's spaCy NER backend."""
    results = _spacy_analyzer.analyze(text=text, language=language)
    return _anonymizer.anonymize(text=text, analyzer_results=results, operators=OPERATORS).text


# =====================================================================
# APPROACH 2 — Presidio + Transformer NER model
# =====================================================================

TRANSFORMERS_AVAILABLE = False
_transformer_analyzer = None

try:
    from presidio_analyzer.nlp_engine import TransformersNlpEngine

    _transformer_model_config = [
        {
            "lang_code": "en",
            "model_name": {
                "spacy": "en_core_web_sm",              # tokeniser only
                "transformers": "dslim/bert-base-NER",   # NER model
            },
        }
    ]
    _transformer_nlp_engine = TransformersNlpEngine(models=_transformer_model_config)
    _transformer_analyzer = AnalyzerEngine(nlp_engine=_transformer_nlp_engine)
    TRANSFORMERS_AVAILABLE = True
except Exception:
    pass  # transformer deps not installed — that's fine, spaCy still works


def redact_transformer(text: str, language: str = "en") -> str:
    """Detect and anonymise PII using a HuggingFace transformer NER model.

    Falls back to spaCy Presidio if transformers are not installed.
    """
    if not TRANSFORMERS_AVAILABLE or _transformer_analyzer is None:
        print("[INFO] Transformer NER not available — using spaCy backend.")
        return redact_spacy(text, language)

    results = _transformer_analyzer.analyze(text=text, language=language)
    return _anonymizer.anonymize(text=text, analyzer_results=results, operators=OPERATORS).text


# =====================================================================
# Unified helper — best-available backend
# =====================================================================

def redact(text: str) -> str:
    """Best-available PII redaction: transformer > spaCy."""
    return redact_transformer(text) if TRANSFORMERS_AVAILABLE else redact_spacy(text)


def scan_output_for_pii(llm_response: str) -> str:
    """Scan LLM output and redact any PII the model may have leaked."""
    return redact(llm_response)


# =====================================================================
# Demo
# =====================================================================

if __name__ == "__main__":
    sample = (
        "Email me at sachin@example.com and call +91 98765-43210. "
        "My SSN is 123-45-6789 and card 4111-1111-1111-1111. "
        "My name is Sachin Dixit and I live at 42 Elm Street."
    )

    # ── spaCy backend ──
    print("=" * 60)
    print("Presidio + spaCy NER")
    print("=" * 60)
    print(redact_spacy(sample))

    print()
    print("Detected entities (spaCy):")
    for r in _spacy_analyzer.analyze(text=sample, language="en"):
        print(f"  {r.entity_type:20s}  score={r.score:.2f}  '{sample[r.start:r.end]}'")

    # ── Transformer backend ──
    print()
    print("=" * 60)
    print("Presidio + Transformer NER (dslim/bert-base-NER)")
    print("=" * 60)
    if TRANSFORMERS_AVAILABLE:
        print(redact_transformer(sample))
        print()
        print("Detected entities (transformer):")
        for r in _transformer_analyzer.analyze(text=sample, language="en"):
            print(f"  {r.entity_type:20s}  score={r.score:.2f}  '{sample[r.start:r.end]}'")
    else:
        print("[Transformer engine not installed — see install instructions above]")

    # ── LLM integration ──
    print()
    print("=" * 60)
    print("LLM call with Presidio PII guard on input + output")
    print("=" * 60)
    user_msg = "My name is Sachin Dixit, email sachin@example.com — summarise my account."
    safe_input = redact(user_msg)
    print(f"User (redacted): {safe_input}")

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Never reveal personal data."},
        {"role": "user", "content": safe_input},
    ]
    response = chat(messages, temperature=0.2)
    safe_output = scan_output_for_pii(response)
    print(f"LLM  (scanned) : {safe_output}")
