
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

class State:
    customer_name: str
    my_age: int

def node_1(state: State):
    if state.get("customer_name") is None:
        state["customer_name"] = "Juan1"
    if state.get("my_age") is None:
        state["my_age"] = 36
    return state

builder = StateGraph(State)
builder.add_node("node_1", node_1)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

agent = builder.compile()
