from langgraph.graph import StateGraph, END
from src.agents.state import CarePathState
from src.agents.router import supervisor_router
from src.agents.nodes.supervisor import supervisor_node
from src.agents.nodes.safety import safety_node
from src.agents.nodes.intake import intake_node
from src.agents.nodes.vision import vision_node
from src.agents.nodes.docs import docs_node
from src.agents.nodes.medication import medication_node
from src.agents.nodes.memory import memory_node
from src.agents.nodes.doctor_bridge import doctor_bridge_node
from src.agents.nodes.timeline import timeline_node
from src.agents.nodes.evidence import evidence_node
from src.agents.nodes.clinical_reasoning import clinical_reasoning_node
from src.agents.nodes.referral import referral_node
from src.agents.nodes.care_plan import care_plan_node
from src.agents.nodes.follow_up import follow_up_node
from src.core.logging import logger


def build_carepath_graph():
    """Builds and compiles the complete multi-agent LangGraph StateGraph."""
    logger.info("building_langgraph_multi_agent_state_graph")
    builder = StateGraph(CarePathState)

    # Register all agent nodes
    builder.add_node("supervisor",         supervisor_node)
    builder.add_node("safety",             safety_node)
    builder.add_node("intake",             intake_node)
    builder.add_node("vision",             vision_node)
    builder.add_node("docs",               docs_node)
    builder.add_node("medication",         medication_node)
    builder.add_node("memory",             memory_node)
    builder.add_node("doctor_bridge",     doctor_bridge_node)
    builder.add_node("timeline",           timeline_node)
    builder.add_node("evidence",           evidence_node)
    builder.add_node("clinical_reasoning", clinical_reasoning_node)
    builder.add_node("referral",           referral_node)
    builder.add_node("care_plan",          care_plan_node)
    builder.add_node("follow_up",          follow_up_node)

    # Entry point
    builder.set_entry_point("supervisor")

    # Every agent loops back to Supervisor after completion
    for node in [
        "safety", "intake", "vision", "docs", "medication", "memory",
        "doctor_bridge", "timeline", "evidence", "clinical_reasoning",
        "referral", "care_plan", "follow_up",
    ]:
        builder.add_edge(node, "supervisor")

    # Supervisor conditional routing
    builder.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "intake":             "intake",
            "safety":             "safety",
            "vision":             "vision",
            "docs":               "docs",
            "medication":         "medication",
            "memory":             "memory",
            "doctor_bridge":     "doctor_bridge",
            "timeline":           "timeline",
            "evidence":           "evidence",
            "clinical_reasoning": "clinical_reasoning",
            "referral":           "referral",
            "care_plan":          "care_plan",
            "follow_up":          "follow_up",
            "__end__":            END,
        },
    )

    return builder.compile()


carepath_graph = build_carepath_graph()
