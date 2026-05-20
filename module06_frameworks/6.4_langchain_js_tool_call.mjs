 

import { ChatOllama } from "@langchain/ollama";
import { tool } from "@langchain/core/tools";
import { ToolMessage } from "@langchain/core/messages";
import { z } from "zod";

const OLLAMA_BASE  = process.env.OLLAMA_BASE  ?? "http://localhost:11434";
const OLLAMA_MODEL = process.env.OLLAMA_MODEL ?? "llama3.1:latest";

// ── Model setup ─────────────────────────────────────────────────────────────
// Python: model = ChatOllama(model=..., base_url=...)
const model = new ChatOllama({ baseUrl: OLLAMA_BASE, model: OLLAMA_MODEL, temperature: 0 });

// ── Tool definition ──────────────────────────────────────────────────────────
// Python: @tool  def get_weather(city): ...
const getWeather = tool(
  async ({ city }) => `${city}: +12°C, partly cloudy`,
  {
    name: "get_weather",
    description: "Return the current temperature for a given city",
    schema: z.object({
      city: z.string().describe("City name, e.g. 'London'"),
    }),
  }
);

// ── Bind tools to model ──────────────────────────────────────────────────────
// Python: model_with_tools = model.bind_tools([get_weather])
const modelWithTools = model.bindTools([getWeather]);

// ── Agent loop ───────────────────────────────────────────────────────────────
// Python: def run_agent(user_message): ...
async function runAgent(userMessage) {
  const messages = [{ role: "user", content: userMessage }];

  // Step 1: ask model (may trigger a tool call)
  // Python: ai_msg = model_with_tools.invoke(messages)
  console.log("— Asking Ollama...");
  const aiMsg = await modelWithTools.invoke(messages);
  messages.push(aiMsg);

  // Step 2: execute any tool calls
  // Python: for tool_call in ai_msg.tool_calls:
  for (const toolCall of aiMsg.tool_calls ?? []) {
    if (toolCall.name === "get_weather") {
      console.log(`— Tool triggered: ${JSON.stringify(toolCall.args)}`);

      // Python: tool_result = get_weather.invoke(tool_call)
      const toolResult = await getWeather.invoke(toolCall.args);
      console.log(`— Tool result: ${toolResult}`);

      // Python: messages.append(tool_result)   [ToolMessage]
      messages.push(new ToolMessage({ content: toolResult, name: toolCall.name, tool_call_id: toolCall.id }));
    }
  }

  // Step 3: get final answer with tool results in context
  // Python: ai_msg = model_with_tools.invoke(messages)
  console.log("— Sending tool results back for final answer...");
  const finalMsg = await modelWithTools.invoke(messages);
  return finalMsg.content;
}

// ── Run ──────────────────────────────────────────────────────────────────────
const userQuestion = "What's the weather in Bogotá, Colombia in celsius?";
console.log("LangChain JS Tool Call — twin of module03_langchain/3.1_tool_call.py");
console.log(`User: ${userQuestion}\n`);

runAgent(userQuestion)
  .then(answer => console.log(`Agent: ${answer}`))
  .catch(err   => { console.error("Error:", err.message); process.exit(1); });
