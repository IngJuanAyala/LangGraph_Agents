
import random

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model

llm = init_chat_model("gpt-4o", temperature=1)

# Namespace fijo y global: TODOS los hilos comparten este mismo perfil.
# Esto es lo que hace que la memoria persista al cambiar de hilo en Studio.
MEMORY_NAMESPACE = ("memory", "user")
PROFILE_KEY = "profile"


class State(MessagesState):
    customer_name: str
    my_age: int


def node_1(state: State, store: BaseStore):
    # 1. Leer el perfil de la memoria COMPARTIDA (no del state del hilo).
    item = store.get(MEMORY_NAMESPACE, PROFILE_KEY)

    if item is None:
        # 2. Primera vez que se usa el agente en cualquier hilo: creamos el perfil
        #    y lo guardamos en el store compartido.
        profile = {"customer_name": "Juan Ayala", "my_age": random.randint(20, 35)}
        store.put(MEMORY_NAMESPACE, PROFILE_KEY, profile)
    else:
        profile = item.value

    # 3. System prompt dinámico alimentado desde la memoria compartida.
    system_prompt = SystemMessage(
        content=(
            "Eres un asistente amable. Estos son los datos que recuerdas del usuario "
            "(memoria compartida entre todas las conversaciones):\n"
            f"- Nombre: {profile['customer_name']}\n"
            f"- Edad: {profile['my_age']}\n"
            "Usa esta información cuando el usuario pregunte por sus datos."
        )
    )

    history = state["messages"]
    ai_message = llm.invoke([system_prompt] + history)

    # Reflejamos el perfil en el state del hilo (opcional, para verlo en Studio).
    return {
        "messages": [ai_message],
        "customer_name": profile["customer_name"],
        "my_age": profile["my_age"],
    }


builder = StateGraph(State)
builder.add_node("node_1", node_1)

builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

agent = builder.compile()
