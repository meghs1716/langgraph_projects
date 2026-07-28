from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def get_order_status(order_id: str) -> str:
    """Fetch order status by order ID."""
    db = {
        "A100": "Shipped, arriving tomorrow",
        "A101": "Out for delivery",
        "A102": "Delivered yesterday"
    }
    return db.get(order_id, "Order not found")

@tool
def get_return_policy():
    """Return the return policy summary."""
    return "Returns are accepted within 7 days if items are unused and in original packaging."

tools = [get_order_status, get_return_policy]
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash",api_key=os.getenv('GEMINI_API_KEY')).bind_tools(tools)

def assistant_node(state: AgentState):
    system = SystemMessage(
        content=(
            "You are a customer support assistant. "
            "Use tools when needed. "
            "If you already have enough information, answer directly."
        )
    )
    response = llm.invoke([system] + list(state["messages"]))
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END
graph = StateGraph(AgentState)
graph.add_node("assistant", assistant_node)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "assistant")
graph.add_conditional_edges("assistant", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "assistant")

app = graph.compile()
result = app.invoke({
    "messages": [
        HumanMessage(content="Where is order A100, and what is your return policy?")
    ]
})
last = result["messages"][-1]

if isinstance(last.content, list):
    for block in last.content:
        if block.get("type") == "text":
            print(block["text"])
else:
    print(last.content)