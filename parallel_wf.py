from langgraph.graph import StateGraph,START,END
from typing import TypedDict

class Batsmen(TypedDict):
    runs:int
    balls:int
    fours:int
    sixes:int
    
    sr:float
    bpb:float
    summary:str
def cal_sr(state:Batsmen)->Batsmen:  
    runs=state['runs']
    balls=state['balls']
    sr=(runs/balls)*100
    return {'sr':sr}
def cal_bpr(state:Batsmen)->Batsmen:
    bpr=state['balls']/(state['fours']+state['sixes'])
    return {'bpb':bpr}
def summary(state:Batsmen)->Batsmen:
    summary=f'''strike rate-{state['sr']},
    balls per runs-{state['bpb']}'''
    return {'summary':summary}

graph=StateGraph(Batsmen)
graph.add_node('calc_sr',cal_sr)
graph.add_node('cal_bpr',cal_bpr)
graph.add_node('summary',summary)


graph.add_edge(START,'calc_sr')
graph.add_edge(START,'cal_bpr')
graph.add_edge('calc_sr','summary')
graph.add_edge('cal_bpr','summary')
graph.add_edge('summary',END)
wf=graph.compile()
intial_state={'balls':100,'runs':50,'fours':6,'sixes':4}
op=wf.invoke(intial_state)
print(op)
