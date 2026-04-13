import os, sys, json, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from tools import search, pdf_ingest, summarize


class ResearchExecutor:
    """Execute a research plan step-by-step using simple tools.

    This executor is intentionally small: each step is dispatched to a tool
    that returns structured output saved to `data/notes/`.
    """
    def __init__(self, data_dir=None):
        base = os.path.join(os.path.dirname(__file__), '..')
        self.data_dir = data_dir or os.path.abspath(os.path.join(base, 'data'))
        os.makedirs(os.path.join(self.data_dir, 'notes'), exist_ok=True)

    def execute_plan(self, plan: dict) -> dict:
        results = {'plan_title': plan.get('title'), 'steps': []}
        for step in plan.get('steps', []):
            action = step.get('action')
            sid = step.get('id')
            if action == 'search':
                out = search.search_web(step.get('description'))
            elif action == 'ingest':
                out = pdf_ingest.ingest_folder(os.path.join(self.data_dir, 'pdfs'))
            elif action in ('extract', 'summarize'):
                out = summarize.summarize_all(os.path.join(self.data_dir, 'pdfs'))
            else:
                out = {'note': f'No tool for action {action}'}
            # persist step result
            fname = os.path.join(self.data_dir, 'notes', f'step_{sid}_{int(time.time())}.json')
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump({'step': step, 'result': out}, f, ensure_ascii=False, indent=2)
            results['steps'].append({'id': sid, 'action': action, 'result_summary': str(out)[:200]})
        return results
