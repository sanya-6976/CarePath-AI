from langgraph.graph import StateGraph, END
from src.agents.state import CarePathState
from src.agents.router import supervisor_router
from src.agents.nodes.supervisor import supervisor_node
from src.agents.nodes.safety import safety_node
from src.agents.nodes.intake import intake_node
from src.agents.nodes.vision import vision_node
from src.agents.nodes.docs import docs_node
from src.agents.nodes.timeline import timeline_node
from src.agents.nodes.evidence import evidence_node
from src.agents.nodes.clinical_reasoning import clinical_reasoning_node
from src.agents.nodes.referral import referral_node
from src.agents.nodes.care_plan import care_plan_node
from src.agents.nodes.follow_up import follow_up_node
from src.core.logging import logger


def build_carepath_graph():
    """
    Builds and compiles the complete multi-agent LangGraph StateGraph for CarePath AI.
    """
    logger.info("building_complete_carepath_multi_agent_graph")
    builder = StateGraph(CarePathState)

    # 1. Add All Agent Nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("safety", safety_node)
    builder.add_node("intake", intake_node)
    builder.add_node("vision", vision_node)
    builder.add_node("docs", docs_node)
    builder.add_node("timeline", timeline_node)
    builder.add_node("evidence", evidence_node)
    builder.add_node("clinical_reasoning", clinical_reasoning_node)
    builder.add_node("referral", referral_node)
    builder.add_node("care_plan", care_plan_node)
    builder.add_node("follow_up", follow_up_node)

    # 2. Set Graph Entrypoint
    builder.set_entry_point("supervisor")

    # 3. Add Edges Back to Supervisor Router
    builder.add_edge("safety", "intake")
    builder.add_edge("intake", "supervisor")
    builder.add_edge("vision", "supervisor")
    builder.add_edge("docs", "supervisor")
    builder.add_edge("timeline", "supervisor")
    builder.add_edge("evidence", "supervisor")
    builder.add_edge("clinical_reasoning", "supervisor")
    builder.add_edge("referral", "supervisor")
    builder.add_edge("care_plan", "supervisor")
    builder.add_edge("follow_up", "supervisor")

    # 4. Supervisor Dynamic Conditional Edges
    builder.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "safety": "safety",
            "vision": "vision",
            "docs": "docs",
            "timeline": "timeline",
            "evidence": "evidence",
            "clinical_reasoning": "clinical_reasoning",
            "referral": "referral",
            "care_plan": "care_plan",
            "follow_up": "follow_up",
            "__end__": END,
        }
    )

    return builder.compile()


carepath_graph = build_carepath_graph()


async def run_carepath_agents(
    session_id: str,
    patient_id: str,
    raw_prompt: str,
    image_urls: list = None,
    doc_urls: list = None
) -> dict:
    """Executes the CarePath multi-agent LangGraph workflow."""
    initial_state = {
        "session_id": session_id,
        "patient_id": patient_id,
        "raw_prompt": raw_prompt,
        "uploaded_image_urls": image_urls or [],
        "uploaded_doc_urls": doc_urls or [],
        "is_emergency": False,
        "emergency_alerts": [],
        "workflow_completed": False,
        "overall_confidence": 1.0,
        "current_agent_id": "supervisor",
        "execution_history": [],
        "clinical_timeline": [],
        "retrieved_evidence": [],
        "differential_specialties": [],
        "historical_context": [],
        "previous_analysis": None,
        "changed_factors": [],
        "new_information": [],
        "missing_information": [],
    }
    return await carepath_graph.ainvoke(initial_state)

async def stream_carepath_agents(
    session_id: str,
    patient_id: str,
    raw_prompt: str,
    image_urls: list = None,
    doc_urls: list = None
):
    """Streams the CarePath multi-agent LangGraph workflow execution."""
    initial_state = {
        "session_id": session_id,
        "patient_id": patient_id,
        "raw_prompt": raw_prompt,
        "uploaded_image_urls": image_urls or [],
        "uploaded_doc_urls": doc_urls or [],
        "is_emergency": False,
        "emergency_alerts": [],
        "workflow_completed": False,
        "overall_confidence": 1.0,
        "current_agent_id": "supervisor",
        "execution_history": [],
        "clinical_timeline": [],
        "retrieved_evidence": [],
        "differential_specialties": [],
        "historical_context": [],
        "previous_analysis": None,
        "changed_factors": [],
        "new_information": [],
        "missing_information": [],
    }
    async for event in carepath_graph.astream(initial_state):
        yield event
