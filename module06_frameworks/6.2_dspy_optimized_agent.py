"""
DSPy Optimized Tool Agent — Compare with module01_raw/1.4_tool_single
======================================================================

WHAT THIS SHOWS (capabilities unique to DSPy):
  1. Signatures       — declarative input→output contracts (no manual prompts)
  2. Modules           — composable building blocks (like PyTorch nn.Module)
  3. Teleprompters     — automatic prompt/few-shot optimization with a metric
  4. Assertions        — runtime constraints the LLM must satisfy

WHY THIS MATTERS vs the raw/LangChain approach:
  • Raw (module01): hand-craft every prompt, hope it works, tweak manually
  • LangChain (module03): better abstraction, but prompts are still static
  • DSPy: define WHAT you want, let the optimizer figure out HOW to prompt

SCENARIO: Same tool-calling weather agent as module01_raw/1.4_tool_single,
          but DSPy optimizes the instruction so the LLM reliably calls the
          tool and formats the answer — demonstrated with a tiny train set.

PREREQUISITES:
  pip install dspy-ai

RUN:
  ollama serve
  python module06_frameworks/6.2_dspy_optimized_agent.py
"""

import os
import dspy

# ---------------------------------------------------------------------------
# 1. Configure DSPy to use local Ollama
# ---------------------------------------------------------------------------
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

lm = dspy.LM(
    model=f"ollama_chat/{OLLAMA_MODEL}",
    api_base=OLLAMA_BASE,
    api_key="",               # not needed for local Ollama
    max_tokens=512,
)
dspy.configure(lm=lm)

# ---------------------------------------------------------------------------
# 2. Define tools (same simulated weather as module01)
# ---------------------------------------------------------------------------

def get_weather(city: str) -> str:
    """Simulated weather lookup — same as module01_raw/1.4_tool_single."""
    return f"{city}: +12°C, partly cloudy"


TOOL_REGISTRY = {"get_weather": get_weather}

# ---------------------------------------------------------------------------
# 3. DSPy Signatures — declarative contracts (no prompt engineering)
# ---------------------------------------------------------------------------

class DecideTool(dspy.Signature):
    """Given a user question, decide which tool to call and with what argument.
    Respond with tool_name and tool_arg only."""

    question: str = dspy.InputField(desc="user's natural-language question")
    tool_name: str = dspy.OutputField(desc="name of the tool to call, e.g. get_weather")
    tool_arg: str = dspy.OutputField(desc="argument for the tool, e.g. city name")


class Summarize(dspy.Signature):
    """Given a user question and a tool result, produce a helpful final answer."""

    question: str = dspy.InputField()
    tool_result: str = dspy.InputField(desc="raw output from the tool")
    answer: str = dspy.OutputField(desc="final natural-language answer")

# ---------------------------------------------------------------------------
# 4. DSPy Module — composable agent pipeline
# ---------------------------------------------------------------------------

class ToolAgent(dspy.Module):
    """
    Two-step agent:
      Step 1 — LLM decides tool + arg  (DecideTool signature)
      Step 2 — execute tool, then LLM summarizes (Summarize signature)

    Compare: module01's run_agent() does the same thing with raw HTTP + manual
    prompt construction.  Here the prompts are generated/optimized by DSPy.
    """

    def __init__(self):
        super().__init__()
        self.decide = dspy.ChainOfThought(DecideTool)
        self.summarize = dspy.ChainOfThought(Summarize)

    def forward(self, question: str):
        # Step 1: decide tool
        decision = self.decide(question=question)
        tool_name = decision.tool_name.strip().lower()
        tool_arg = decision.tool_arg.strip()

        # Step 2: execute tool
        tool_fn = TOOL_REGISTRY.get(tool_name)
        if tool_fn is None:
            return dspy.Prediction(answer=f"Unknown tool: {tool_name}")
        tool_result = tool_fn(tool_arg)

        # Step 3: summarize
        summary = self.summarize(question=question, tool_result=tool_result)
        return dspy.Prediction(
            tool_name=tool_name,
            tool_arg=tool_arg,
            tool_result=tool_result,
            answer=summary.answer,
        )

# ---------------------------------------------------------------------------
# 5. (Optional) Optimize with a metric + tiny training set
#    This is the DSPy superpower: automatic prompt tuning
# ---------------------------------------------------------------------------

TRAIN_EXAMPLES = [
    dspy.Example(
        question="What's the weather in Tokyo?",
        tool_name="get_weather",
        tool_arg="Tokyo",
    ).with_inputs("question"),
    dspy.Example(
        question="Tell me the weather in London please",
        tool_name="get_weather",
        tool_arg="London",
    ).with_inputs("question"),
    dspy.Example(
        question="How is the weather in Mumbai right now?",
        tool_name="get_weather",
        tool_arg="Mumbai",
    ).with_inputs("question"),
]


def tool_selection_metric(example, prediction, trace=None) -> float:
    """Metric: did the LLM pick the right tool and argument?"""
    name_ok = prediction.tool_name.strip().lower() == example.tool_name.strip().lower()
    arg_ok = prediction.tool_arg.strip().lower() == example.tool_arg.strip().lower()
    return float(name_ok and arg_ok)


def optimize_agent() -> ToolAgent:
    """Use DSPy BootstrapFewShot to auto-optimize the agent prompts."""
    agent = ToolAgent()
    optimizer = dspy.BootstrapFewShot(
        metric=tool_selection_metric,
        max_bootstrapped_demos=2,
        max_labeled_demos=3,
    )
    optimized = optimizer.compile(agent, trainset=TRAIN_EXAMPLES)
    print("Optimization complete — prompts auto-tuned with few-shot examples.\n")
    return optimized

# ---------------------------------------------------------------------------
# 6. Main — run unoptimized vs optimized to show the difference
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== DSPy Optimized Tool Agent (compare with module01_raw/1.4_tool_single) ===\n")

    question = "What's the weather in Bogotá, Colombia in celsius?"

    # --- Baseline (no optimization) ---
    print("--- Baseline (no optimization) ---")
    baseline = ToolAgent()
    result = baseline(question=question)
    print(f"  Tool:   {result.tool_name}({result.tool_arg})")
    print(f"  Result: {result.tool_result}")
    print(f"  Answer: {result.answer}\n")

    # --- Optimized (auto-tuned prompts) ---
    print("--- Optimized (auto-tuned prompts via BootstrapFewShot) ---")
    try:
        optimized = optimize_agent()
        result = optimized(question=question)
        print(f"  Tool:   {result.tool_name}({result.tool_arg})")
        print(f"  Result: {result.tool_result}")
        print(f"  Answer: {result.answer}\n")
    except Exception as exc:
        print(f"  Optimization skipped ({exc})")
        print("  This can happen if the local model doesn't support enough")
        print("  demonstrations.  The baseline above still works.\n")

    print("KEY TAKEAWAY: DSPy replaces manual prompt engineering with")
    print("declarative signatures + automatic optimization.  You define")
    print("WHAT the LLM should produce, not HOW to ask for it.")
