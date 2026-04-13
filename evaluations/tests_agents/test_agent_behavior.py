
import json

def controller_out(model_out: str):
    try:
        proposal = json.loads(model_out)
        tool = proposal.get('tool'); args = proposal.get('args',{})
        if tool == 'add':
            return args.get('a',0)+args.get('b',0)
    except json.JSONDecodeError:
        return model_out

def test_tool_json_parsed():
    mo = json.dumps({'tool':'add','args':{'a':2,'b':3}})
    assert controller_out(mo)==5

def test_direct_answer_passthrough():
    mo = 'No tool needed.'
    assert controller_out(mo)==mo
