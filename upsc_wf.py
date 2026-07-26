from langgraph.graph import START,END,StateGraph
from typing import TypedDict,Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
import operator
from pydantic import BaseModel,Field
import os
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=os.getenv('GEMINI_API_KEY'))
#state
#3 nodes-> JSON format
#parallel connect
class Json(BaseModel):
    feedback:str=Field(description='detatiled feedback for score')
    score:int=Field(description='score out of 10,ge=0,le=10')
structured_model=model.with_structured_output(Json)
class UPSCstate(TypedDict):
    essay:str
    lf:str
    analysis_f:str
    clarity_of:str
    overall_feedback:str
    individual_score:Annotated[list[int], operator.add]
    avg_scores:float
def eval_language(state:UPSCstate):
    prompt=f'''eval the language quality of the essay,and give feedback also, give a score between(0-10) essay : {state['essay']} '''
    op=structured_model.invoke(prompt)
    return {'lf':op.feedback,'individual_score':[op.score]}
def eval_analysis(state:UPSCstate):
    prompt=f''' evaluate the depth of analysis of the essay also provide a score(0-10), essay:{state['essay']} '''
    op=structured_model.invoke(prompt)
    return{'analysis_f':op.feedback,'individual_score':[op.score]}

def eval_cot(state:UPSCstate):
    prompt=f''' evaluate the clarity of thought of the essay also provide a score(0-10), essay:{state['essay']} '''
    op=structured_model.invoke(prompt)
    return{'clarity_of':op.feedback,'individual_score':[op.score]}
    
def final_eval(state:UPSCstate):
    #summary
    #avg scores
    prompt=f'''Based on the following feedback,create a summarized feedback: {state["lf"]}  ,{state["analysis_f"]},{state["clarity_of"]}'''
    op=model.invoke(prompt).content
    avg_scores=sum(state['individual_score'])/len(state['individual_score'])
    
    return{'overall_feedback':op,'avg_scores':avg_scores}


graph=StateGraph(UPSCstate)
graph.add_node('eval_language',eval_language)
graph.add_node('eval_analysis',eval_analysis)
graph.add_node('eval_cot',eval_cot)
graph.add_node('final_eval',final_eval)
    
graph.add_edge(START,eval_language)
graph.add_edge(START,eval_analysis)
graph.add_edge(START,eval_cot)

graph.add_edge('eval_language','final_eval')
graph.add_edge('eval_analysis','final_eval')
graph.add_edge('eval_cot','final_eval')
graph.add_edge('final_eval',END)

hm=graph.compile()
initial_state={'essay':'Mothers Day is a special global celebration honoring maternal bonds, unconditional love, and the immense sacrifices mothers make. Observed annually on the second Sunday of May, it is a time for people worldwide to express deep gratitude and appreciation for the mother figures in their lives.'}
final_state=hm.invoke(initial_state)
print(final_state)