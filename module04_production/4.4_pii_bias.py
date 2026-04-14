import re
from utils.ollama_client import chat


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
CREDIT_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

SENSITIVE_GROUPS = ["race", "religion", "gender", "ethnicity", "nationality"]

def redact(text: str) -> str:
    """Redact common PII patterns. This is not exhaustive."""
    text = EMAIL.sub("[EMAIL_REDACTED]", text)
    text = PHONE.sub("[PHONE_REDACTED]", text)
    text = CREDIT_CARD.sub("[CARD_REDACTED]", text)
    text = SSN.sub("[SSN_REDACTED]", text)
    return text

def is_sensitive_comparison(text: str) -> bool:
    """Block comparative questions involving sensitive attributes."""
    lowered = text.lower()
    if any(g in lowered for g in SENSITIVE_GROUPS) and ("better" in lowered or "worse" in lowered):
        return True
    return False

def scan_output_for_pii(llm_response: str) -> str:
    """Scan LLM output and redact any PII the model may have leaked."""
    return redact(llm_response)


BIAS_INSTRUCTIONS = (
    "Avoid stereotypes and be neutral. If a request seems biased, ask clarifying questions "
    "and avoid harmful generalizations. Never include personal data like email addresses, "
    "phone numbers, or credit card numbers in your responses."
)

if __name__ == "__main__":
    user = "Email me at sachin@example.com and call +91 98765-43210. Does HR or Engineering earn more?"
    if is_sensitive_comparison(user):
        print("I can help with general info, but I can’t compare groups in a sensitive way.")
    else:
        safe = redact(user)
        messages = [
            {"role": "system", "content": BIAS_INSTRUCTIONS},
            {"role": "user", "content": safe},
        ]
        response = chat(messages, temperature=0.2)
        # Also scan the LLM output for any PII leakage
        safe_response = scan_output_for_pii(response)
        print(safe_response)
