"""PII Detection — LangChain Integration

LangChain provides two complementary PII mechanisms:

  1. **PresidioReversibleAnonymizer** (`langchain_experimental`)
     Wraps Microsoft Presidio to anonymise text *before* it reaches the LLM,
     then **de-anonymises** the response — so the model reasons over fake
     placeholder names but the final output restores the real ones.
     Great when the LLM needs contextual understanding of entities without
     ever seeing the real PII.

  2. **PIIMiddleware** (`langchain.agents.middleware`)
     Declarative middleware applied at the agent level.  It intercepts
     messages *before* the model, *after* the model, or *after tool calls*
     and applies a strategy: ``redact``, ``mask``, ``hash``, or ``block``.
     Built-in detectors for email, credit_card, IP, mac_address, URL.
     Custom regex or function detectors for anything else (SSN, API keys …).

Install (one-time):
    pip install langchain langchain-experimental langchain-ollama
    pip install presidio-analyzer presidio-anonymizer
    python -m spacy download en_core_web_lg

Progression:
  4.4  Regex baseline
  4.5  Presidio (spaCy + transformer NER models)
  4.6  LangChain PII middleware & reversible anonymiser ← you are here
  4.7  Bias guardrails
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# =====================================================================
# APPROACH 1 — Reversible Anonymiser (anonymise → LLM → de-anonymise)
# =====================================================================
# The LLM never sees real PII; afterwards the real values are swapped back.
# Use case: you need the model to reason about entities, but must not
# expose PII to the inference provider.

try:
    from langchain_experimental.data_anonymizer import (
        PresidioAnonymizer,
        PresidioReversibleAnonymizer,
    )

    ANONYMIZER_AVAILABLE = True
except ImportError:
    ANONYMIZER_AVAILABLE = False


def demo_reversible_anonymizer() -> None:
    """Show anonymise → LLM → de-anonymise round-trip."""
    if not ANONYMIZER_AVAILABLE:
        print("[WARN] langchain_experimental not installed — skipping reversible anonymiser demo.")
        return

    anonymizer = PresidioReversibleAnonymizer(languages_config={"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]})

    original = (
        "Sachin Dixit's email is sachin@example.com and his phone is +91 98765-43210. "
        "His SSN is 123-45-6789."
    )

    # Anonymise — real names/emails replaced with synthetic ones
    anonymized_text = anonymizer.anonymize(original)
    print("Anonymised text sent to LLM:")
    print(f"  {anonymized_text}")
    print()

    # Show the mapping Presidio keeps internally
    print("Anonymisation mapping (kept for de-anonymisation):")
    for entity_type, mapping in anonymizer.deanonymizer_mapping.items():
        for fake, real in mapping.items():
            print(f"  {entity_type:20s}  {fake} → {real}")
    print()

    # LLM call — model only sees anonymised text
    llm = ChatOllama(model="llama3.2:latest", base_url="http://localhost:11434")
    prompt = f"Summarise this customer record in one sentence:\n\n{anonymized_text}"
    llm_response = llm.invoke([HumanMessage(content=prompt)])
    print(f"LLM response (with fake names): {llm_response.content}")

    # De-anonymise — restore real entities in the LLM output
    restored = anonymizer.deanonymize(llm_response.content)
    print(f"De-anonymised output          : {restored}")


# =====================================================================
# APPROACH 2 — PIIMiddleware on a LangChain Agent
# =====================================================================
# Declarative: just list detectors + strategies when creating the agent.
# Supports: redact, mask, hash, block.
# Applied to: input, output, or tool results.

try:
    from langchain.agents import create_agent
    from langchain.agents.middleware import PIIMiddleware

    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False


def demo_pii_middleware() -> None:
    """Show PIIMiddleware redacting/masking PII before the model sees it."""
    if not MIDDLEWARE_AVAILABLE:
        print("[WARN] langchain PIIMiddleware not available — skipping middleware demo.")
        return

    llm = ChatOllama(model="llama3.2:latest", base_url="http://localhost:11434")

    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[
            # Redact emails in user input before sending to model
            PIIMiddleware("email", strategy="redact", apply_to_input=True),
            # Mask credit card numbers
            PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
            # Block API keys — raises an error if detected in input
            PIIMiddleware(
                "api_key",
                detector=r"sk-[a-zA-Z0-9]{32,}",
                strategy="block",
                apply_to_input=True,
            ),
            # Also scan model output for leaked PII
            PIIMiddleware("email", strategy="redact", apply_to_output=True),
        ],
    )

    test_input = (
        "My email is sachin@example.com and my card is 4111-1111-1111-1111. "
        "Please summarise my account."
    )
    print(f"User input    : {test_input}")
    result = agent.invoke({"messages": [HumanMessage(content=test_input)]})
    print(f"Agent response: {result['messages'][-1].content}")


# =====================================================================
# Demo
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DEMO 1 — Reversible Anonymiser (anonymise → LLM → de-anonymise)")
    print("=" * 60)
    demo_reversible_anonymizer()

    print()
    print("=" * 60)
    print("DEMO 2 — PIIMiddleware on a LangChain Agent")
    print("=" * 60)
    demo_pii_middleware()
