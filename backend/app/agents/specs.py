"""
CarePath AI - Agent Specifications Registry
===========================================
Defines the architectural contract, responsibilities, tools, and error handling
rules for all 11 agents in the Multi-Agent Navigation System.
"""

from typing import Dict, List, Any
from pydantic import BaseModel


class AgentSpecification(BaseModel):
    agent_id: str
    name: str
    responsibility: str
    inputs: List[str]
    outputs: List[str]
    tools_used: List[str]
    state_updates: List[str]
    prompt_strategy: str
    error_handling: str
    success_criteria: str
    failure_criteria: str
    next_possible_agents: List[str]


AGENT_SPECIFICATIONS: Dict[str, AgentSpecification] = {
    "SUPERVISOR": AgentSpecification(
        agent_id="SUPERVISOR",
        name="Supervisor Orchestrator Agent",
        responsibility="Acts as the central brain. Evaluates state, inspects user payloads, routes work dynamically, triggers parallel worker execution, handles missing information, and enforces early exit on emergencies.",
        inputs=["raw_prompt", "uploaded_image_urls", "uploaded_doc_urls", "is_emergency", "overall_confidence"],
        outputs=["current_agent_id", "execution_history", "missing_information"],
        tools_used=["evaluate_state_tool", "route_graph_tool"],
        state_updates=["current_agent_id", "workflow_completed"],
        prompt_strategy="Zero-shot reasoning over graph state context with strict JSON routing outputs.",
        error_handling="Fallback to Safety Agent if routing fails or state is corrupted.",
        success_criteria="Selects valid next agent node or terminates workflow cleanly.",
        failure_criteria="Cycles infinitely or routes to undefined agent node.",
        next_possible_agents=["SAFETY", "INTAKE", "VISION", "DOCS", "CLINICAL_REASONING", "CARE_PLAN", "END"]
    ),

    "INTAKE": AgentSpecification(
        agent_id="INTAKE",
        name="Intake & Triage Agent",
        responsibility="Parses unstructured patient chief complaints into structured medical symptom objects, severity ratings, and body locations.",
        inputs=["raw_prompt"],
        outputs=["structured_symptoms"],
        tools_used=["nlp_symptom_parser_tool"],
        state_updates=["structured_symptoms"],
        prompt_strategy="Structured extraction specifying chief complaint, duration, severity scale (1-10), and location.",
        error_handling="Populate default symptom object with confidence score < 0.3 if extraction fails.",
        success_criteria="Successfully populates StructuredSymptom model with > 80% confidence.",
        failure_criteria="Fails to identify any symptoms or duration from prompt.",
        next_possible_agents=["SUPERVISOR", "SAFETY"]
    ),

    "VISION": AgentSpecification(
        agent_id="VISION",
        name="Vision Analysis Agent",
        responsibility="Analyzes uploaded medical photos (dermatology lesions, x-rays, visible swelling) via Vision API adapter.",
        inputs=["uploaded_image_urls"],
        outputs=["vision_findings"],
        tools_used=["computer_vision_api_tool"],
        state_updates=["vision_findings"],
        prompt_strategy="Multimodal prompt requesting anatomical region, lesion features, and image quality assessment.",
        error_handling="Flags image_quality_score < 0.5 and logs warning for re-upload.",
        success_criteria="Returns visual observations and anatomical identification.",
        failure_criteria="Image corrupt or unrecognized format.",
        next_possible_agents=["SUPERVISOR", "SAFETY"]
    ),

    "DOCS": AgentSpecification(
        agent_id="DOCS",
        name="Medical Docs & Lab Agent",
        responsibility="Processes PDF lab reports, discharge summaries, and prescriptions via OCR & document parser APIs.",
        inputs=["uploaded_doc_urls"],
        outputs=["parsed_docs"],
        tools_used=["ocr_document_api_tool"],
        state_updates=["parsed_docs"],
        prompt_strategy="Key-value extraction of lab ranges, ICD-10 codes, and abnormal flags.",
        error_handling="Fallback to raw OCR string if key-value parsing fails.",
        success_criteria="Successfully extracts lab values and flag abnormal items.",
        failure_criteria="Unreadable PDF scan or missing text layer.",
        next_possible_agents=["SUPERVISOR", "TIMELINE"]
    ),

    "TIMELINE": AgentSpecification(
        agent_id="TIMELINE",
        name="Chronological Timeline Agent",
        responsibility="Orders symptoms, doc uploads, and prior clinical events chronologically to construct a holistic patient history.",
        inputs=["structured_symptoms", "parsed_docs"],
        outputs=["clinical_timeline"],
        tools_used=["timeline_sorter_tool"],
        state_updates=["clinical_timeline"],
        prompt_strategy="Temporal extraction and alignment of events into an array of Dated Clinical Events.",
        error_handling="Assign relative order (e.g. Day -3, Today) if absolute dates are missing.",
        success_criteria="Generates a sorted chronological timeline list.",
        failure_criteria="Inconsistent or contradictory temporal sequencing.",
        next_possible_agents=["SUPERVISOR", "EVIDENCE"]
    ),

    "EVIDENCE": AgentSpecification(
        agent_id="EVIDENCE",
        name="Clinical Evidence RAG Agent",
        responsibility="Queries Vector DB (ChromaDB) for official clinical guidelines (CDC, WHO, PubMed, Specialty Guidelines) matching patient profile.",
        inputs=["structured_symptoms", "parsed_docs"],
        outputs=["retrieved_evidence"],
        tools_used=["chroma_vector_search_tool"],
        state_updates=["retrieved_evidence"],
        prompt_strategy="Vector embedding search using symptom embeddings filtered by medical domain.",
        error_handling="Fallback to broad general practice guidelines if similarity score < 0.6.",
        success_criteria="Retrieves top 3 relevant peer-reviewed clinical guidelines.",
        failure_criteria="Vector database unreachable or empty result.",
        next_possible_agents=["SUPERVISOR", "CLINICAL_REASONING"]
    ),

    "CLINICAL_REASONING": AgentSpecification(
        agent_id="CLINICAL_REASONING",
        name="Clinical Reasoning Agent",
        responsibility="Synthesizes symptoms, vision, lab findings, and retrieved evidence into a differential list of recommended specialist disciplines.",
        inputs=["structured_symptoms", "vision_findings", "parsed_docs", "retrieved_evidence"],
        outputs=["differential_specialties", "overall_confidence"],
        tools_used=["clinical_synthesis_tool"],
        state_updates=["differential_specialties", "overall_confidence"],
        prompt_strategy="Chain-of-Thought (CoT) medical reasoning linking findings to medical specialties.",
        error_handling="Request human review / trigger missing information state if confidence < 0.5.",
        success_criteria="Produces top 2-3 matching medical specialties with confidence scores.",
        failure_criteria="Hallucinates non-existent diagnoses or conflicting specialties.",
        next_possible_agents=["SUPERVISOR", "REFERRAL"]
    ),

    "REFERRAL": AgentSpecification(
        agent_id="REFERRAL",
        name="Specialist Referral Agent",
        responsibility="Formulates triage level (Urgent vs Routine) and crafts custom questions for the patient to ask their specialist.",
        inputs=["differential_specialties", "structured_symptoms"],
        outputs=["referral_recommendation"],
        tools_used=["referral_formatter_tool"],
        state_updates=["referral_recommendation"],
        prompt_strategy="Triage matrix mapping specialty urgency to patient safety guidelines.",
        error_handling="Default to URGENT_48HRS if triage score is ambiguous.",
        success_criteria="Provides clear specialty recommendation, urgency tier, and 3 specific doctor questions.",
        failure_criteria="Missing triage urgency classification.",
        next_possible_agents=["SUPERVISOR", "CARE_PLAN"]
    ),

    "SAFETY": AgentSpecification(
        agent_id="SAFETY",
        name="Safety & Red Flag Agent",
        responsibility="Scans all inputs continuously for red flags (chest pain, stroke, severe bleeding) and triggers 911 emergency bypass.",
        inputs=["raw_prompt", "structured_symptoms", "vision_findings", "parsed_docs"],
        outputs=["is_emergency", "emergency_alerts"],
        tools_used=["red_flag_scanner_tool"],
        state_updates=["is_emergency", "emergency_alerts", "workflow_completed"],
        prompt_strategy="Zero-shot red flag heuristic checker across vital red flag categories.",
        error_handling="Trigger conservative emergency alert on any doubt.",
        success_criteria="Accurately identifies red flags or verifies emergency clearance.",
        failure_criteria="False negative on a life-threatening symptom.",
        next_possible_agents=["END"]
    ),

    "CARE_PLAN": AgentSpecification(
        agent_id="CARE_PLAN",
        name="Patient Care Plan Agent",
        responsibility="Generates plain-language prep steps, tracking logs, and non-diagnostic symptom monitoring guides for the patient.",
        inputs=["referral_recommendation", "structured_symptoms", "parsed_docs"],
        outputs=["care_plan"],
        tools_used=["care_plan_generator_tool"],
        state_updates=["care_plan"],
        prompt_strategy="Patient-centered, 6th-grade reading level translation with action items.",
        error_handling="Fallback to generic prep checklist if synthesis fails.",
        success_criteria="Produces readable, empathetic care plan with clear next steps.",
        failure_criteria="Contains medical jargon without explanation.",
        next_possible_agents=["SUPERVISOR", "FOLLOWUP"]
    ),

    "FOLLOW_UP": AgentSpecification(
        agent_id="FOLLOW_UP",
        name="Follow-up & Reminders Agent",
        responsibility="Schedules automated follow-up check-ins (e.g. in 48h) to re-assess patient symptoms and appointment status.",
        inputs=["care_plan", "referral_recommendation"],
        outputs=["followup_scheduled"],
        tools_used=["scheduler_service_tool"],
        state_updates=["followup_scheduled", "workflow_completed"],
        prompt_strategy="Cron and reminder payload construction based on triage urgency.",
        error_handling="Log reminder error and complete workflow safely.",
        success_criteria="Registers follow-up task timestamp in state.",
        failure_criteria="Fails to generate valid ISO date for follow-up.",
        next_possible_agents=["END"]
    )
}
