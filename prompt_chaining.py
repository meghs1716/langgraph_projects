from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
model = ChatGoogleGenerativeAI(model="gemini-2.5-pro",api_key=os.getenv('GEMINI_API_KEY'))
class BLOG(TypedDict):
    title:str
    outline:str
    content:str
def create_outline(state:BLOG)->BLOG:
    title=state['title']
    prompt=f'generate an outline for a blog on title-{title}'
    outline=model.invoke(prompt).content
    state['outline']=outline
    return state
#fetching title and creating an ouline
def create_blog(state:BLOG)->BLOG:
    title=state['title']
    outline=state['outline']
    prompt=f'create content for a blog in 10 words based on the outline-{outline}'
    content=model.invoke(prompt).content
    state['content']=content
    return state

#based on the outline stored in state, creating an content
graph=StateGraph(BLOG)
graph.add_node('blog_create',create_outline)
graph.add_node('create_blog',create_blog)

graph.add_edge(START,'blog_create')
graph.add_edge('blog_create','create_blog')
graph.add_edge('create_blog',END)

wf=graph.compile()
initial_state={'title':'UPSC EXAM'}
fs=wf.invoke(initial_state)
print(fs)