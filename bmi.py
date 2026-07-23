from langgraph.graph import StateGraph,START,END
from typing import TypedDict
class BMI(TypedDict):
    weight_kg:float
    height_m:float
    result:float
    category:str
#define a graph
def calc(state:BMI)->BMI:# type is state
    ''' calculate the bmi of given weights and height'''
    weight=state['weight_kg']
    height=state['height_m']
    result=weight/(height**2)
    state['result']=round(result,2)
    return state
def label_emi(state:BMI):
    bmi=state['result']
    if bmi<18.5:
        state['category']='underweight'
    elif 18.5<=bmi<25:
        state['category']='normal'
    elif 25<=bmi<30:
        state['category']='overweight'
    else:
        state['category']='obese'
graph=StateGraph(BMI)
graph.add_node("bmi_calc",calc)
graph.add_node("bmi_label",label_emi)

graph.add_edge(START,'bmi_calc')
graph.add_edge('bmi_calc','bmi_label')
graph.add_edge('bmi_label',END)


wf=graph.compile()
op=wf.invoke({'weight_kg':48,'height_m':1.65})
print(op)