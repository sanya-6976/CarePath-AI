"""Small LangGraph workflow for the patient-facing companion.

It is intentionally isolated from the clinical 11-agent graph: this graph only
receives already-authorized, retrieved context and a response prepared by the
companion agent. It never performs diagnosis or changes a clinical record.
"""
from typing import TypedDict
from langgraph.graph import END, StateGraph


class CompanionState(TypedDict):
    context: dict
    answer: str
    language: str


def _ground_response(state: CompanionState) -> dict:
    # Explicit graph boundary: only the supplied, ownership-scoped context moves
    # through this workflow. The response is generated before this handoff.
    return {"answer": state["answer"]}


def build_companion_graph():
    graph = StateGraph(CompanionState)
    graph.add_node("ground_response", _ground_response)
    graph.set_entry_point("ground_response")
    graph.add_edge("ground_response", END)
    return graph.compile()


companion_graph = build_companion_graph()


def run_companion_workflow(context: dict, answer: str, language: str) -> str:
    return companion_graph.invoke({"context": context, "answer": answer, "language": language})["answer"]
