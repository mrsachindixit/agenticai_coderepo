"""Bias Guardrails — Detecting and Blocking Biased Prompts

Simple guardrails that intercept user prompts and block or rewrite
requests that ask the model to make comparative judgements involving
sensitive demographic attributes (race, religion, gender, …).

In a production pipeline these checks sit *before* the LLM call —
right after PII redaction and before the system prompt is assembled.

Progression:
  4.4  Regex PII baseline
  4.5  Presidio PII (spaCy + transformer NER models)
  4.6  LangChain PII middleware & reversible anonymiser
  4.7  Bias guardrails ← you are here
"""

from utils.ollama_client import chat

# ── Sensitive-group vocabulary ─────────────────────────────────────

SENSITIVE_GROUPS = ["race", "religion", "gender", "ethnicity", "nationality"]

COMPARATIVE_WORDS = ["better", "worse", "superior", "inferior", "smarter", "dumber"]


def is_sensitive_comparison(text: str) -> bool:
    """Return True if the text asks the model to rank sensitive groups."""
    lowered = text.lower()
    has_group = any(g in lowered for g in SENSITIVE_GROUPS)
    has_compare = any(c in lowered for c in COMPARATIVE_WORDS)
    return has_group and has_compare


BIAS_INSTRUCTIONS = (
    "Avoid stereotypes and be neutral. If a request seems biased, ask "
    "clarifying questions and avoid harmful generalizations. Never include "
    "personal data like email addresses, phone numbers, or credit card "
    "numbers in your responses."
)


def safe_chat(user_message: str, temperature: float = 0.2) -> str:
    """Chat wrapper that blocks biased comparisons and prepends bias-aware
    system instructions for everything else."""
    if is_sensitive_comparison(user_message):
        return (
            "I can help with general info, but I can't compare groups "
            "in a sensitive or potentially harmful way."
        )

    messages = [
        {"role": "system", "content": BIAS_INSTRUCTIONS},
        {"role": "user", "content": user_message},
    ]
    return chat(messages, temperature=temperature)


# ── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":

    test_cases = [
        "Which gender is better at coding?",
        "Is one ethnicity smarter than another?",
        "What are the main programming paradigms?",
        "Does HR or Engineering earn more?",
    ]

    for user_msg in test_cases:
        print("=" * 60)
        print(f"User: {user_msg}")
        print("-" * 60)
        if is_sensitive_comparison(user_msg):
            print("[BLOCKED] Sensitive comparison detected.")
        else:
            print("[ALLOWED] Forwarding to LLM …")
        response = safe_chat(user_msg)
        print(f"Response: {response}")
        print()
