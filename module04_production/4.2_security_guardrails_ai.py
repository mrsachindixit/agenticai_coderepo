# Security Guardrails — Guardrails AI Framework
# pip install guardrails-ai

try:
    from guardrails import Guard, OnFailAction
    from guardrails.hub import RegexMatch, ValidLength, ToxicLanguage, DetectPII
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False


# --- Input validation with chained validators ---

def create_name_guard() -> "Guard":
    return Guard().use_many(
        RegexMatch(regex=r"^[A-Z][a-z]+$", on_fail=OnFailAction.NOOP),
        ValidLength(min=2, max=50, on_fail=OnFailAction.NOOP),
    )


# --- Toxic language detection ---

def create_toxicity_guard() -> "Guard":
    # Classifier-based, not regex — catches nuanced toxicity
    return Guard().use(
        ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail=OnFailAction.EXCEPTION)
    )


# --- PII detection on prompts (block if PII found) ---

def create_pii_input_guard() -> "Guard":
    guard = Guard()
    guard.use(
        DetectPII(
            pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"],
            on_fail=OnFailAction.EXCEPTION,
        ),
        on="prompt",
    )
    return guard


# --- Validate LLM output against a Guard ---

def validate_output(guard: Guard, llm_output: str) -> dict:
    result = guard.validate(llm_output)
    return {
        "passed": result.validation_passed,
        "output": result.validated_output,
        "error": str(result.error) if result.error else None,
    }


if __name__ == "__main__":
    if not GUARDRAILS_AVAILABLE:
        print("Install: pip install guardrails-ai")
        print("Then:    guardrails hub install hub://guardrails/regex_match")
        print("         guardrails hub install hub://guardrails/valid_length")
        print("         guardrails hub install hub://guardrails/toxic_language")
        print("         guardrails hub install hub://guardrails/detect_pii")
        raise SystemExit(1)

    # Name validation
    name_guard = create_name_guard()
    print("'Caesar' valid:", name_guard.validate("Caesar").validation_passed)
    print("'caesar salad' valid:", name_guard.validate("caesar salad").validation_passed)

    # Toxicity check
    toxicity_guard = create_toxicity_guard()
    print()
    try:
        toxicity_guard.validate("You are a wonderful assistant!")
        print("Clean text: passed")
    except Exception as e:
        print(f"Clean text blocked: {e}")

    try:
        toxicity_guard.validate("You are an absolute idiot!")
        print("Toxic text: passed (unexpected)")
    except Exception:
        print("Toxic text: blocked (expected)")

    # PII in prompt
    pii_guard = create_pii_input_guard()
    print()
    print("PII guard created — blocks emails/phones/cards in prompts")
    result = validate_output(name_guard, "Caesar")
    print(f"Validate output: {result}")
