from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
from langgraph.checkpoint.memory import InMemorySaver
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash",api_key=os.getenv('GEMINI_API_KEY'))
class Joke(TypedDict):
    topic:str
    joke:str
    explaination:str
def generate_joke(state:Joke):
    prompt=f'''generate a witty come back on the topic:{state['topic']}'''
    res=llm.invoke(prompt).content
    return {'joke':res}
def explain_joke(state:Joke):
    prompt=f'''explain the reasoning behind the comeback:{state['joke']}'''
    res=llm.invoke(prompt).content
    return {'explaination':res}
graph=StateGraph(Joke)
graph.add_node("gen_joke",generate_joke)
graph.add_node("explain_joke",explain_joke)
graph.add_edge(START,'gen_joke')
graph.add_edge('gen_joke','explain_joke')
graph.add_edge("explain_joke",END)
checkpointer=InMemorySaver()
wf=graph.compile(checkpointer=checkpointer)
config={'configurable':{'thread_id':1}}
result=wf.invoke({'topic':'pizza'},config=config)
print(result)