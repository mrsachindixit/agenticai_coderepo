

import logging
import time
import uuid
from langchain_community.chat_models import ChatOllama
from langchain.callbacks.base import BaseCallbackHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

class SimpleLogger(BaseCallbackHandler):
    def on_llm_start(self, *args, **kwargs):
        self.start = time.time()
        self.req_id = str(uuid.uuid4())
        logging.info("req_id=%s LLM start", self.req_id)
        prompts = kwargs.get("prompts")
        if prompts:
            logging.info("req_id=%s prompt_preview=%s", self.req_id, prompts[0][:200])

    def on_llm_end(self, *args, **kwargs):
        elapsed = time.time() - self.start
        logging.info("req_id=%s LLM end elapsed=%.2fs", self.req_id, elapsed)

    def on_llm_error(self, *args, **kwargs):
        logging.exception("req_id=%s LLM error", getattr(self, "req_id", "unknown"))


def log_tool_call(tool_name: str, payload: dict, result: str):
    """Basic tool call logging hook."""
    logging.info("tool=%s payload=%s result_preview=%s", tool_name, payload, result[:200])


if __name__ == "__main__":
    llm = ChatOllama(model="llama3.2", temperature=0.2, callbacks=[SimpleLogger()])
    resp = llm.invoke("In one line, what is an agent?")
    logging.info("Response: %s", resp.content)

    # Example tool call logging
    log_tool_call("mock_tool", {"q": "agents"}, "ok")

