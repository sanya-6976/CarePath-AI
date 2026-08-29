import { AgentSpec, ApiEndpointSpec, BlueprintTopic, FolderNode } from "../types";

export const AGENT_SPECS: AgentSpec[] = [
  {
    id: "supervisor_agent",
    name: "Supervisor Agent",
    role: "Dynamic Graph Router & Task Allocator",
    color: "#6366f1",
    description: "Evaluates current global graph state, incoming artifacts, and execution metrics to dynamically compute next agent nodes or terminate workflow.",
    input_keys: ["patient_symptoms", "uploaded_files", "agent_outputs", "emergency_flags"],
    output_keys: ["next_agent", "execution_plan", "is_complete"],
    model_tier: "Gemini 2.5 Flash / Pro (Orchestrator)",
    fallback_strategy: "Static Fallback Route -> Safety Agent -> Intake Agent",
    rag_enabled: false
  },
  {
    id: "intake_agent",
    name: "Intake Agent",
    role: "Symptom & History Harvester",
    color: "#3b82f6",
    description: "Extracts structured clinical symptoms, duration, severity scale (1-10), aggravating factors, and demographic context.",
    input_keys: ["raw_user_prompt", "conversation_history"],
    output_keys: ["structured_symptoms", "chief_complaint", "severity_score"],
    model_tier: "Gemini 2.5 Flash (NLP Extractor)",
    fallback_strategy: "Regenerate with Structured Pydantic Output Parser",
    rag_enabled: false
  },
  {
    id: "vision_agent",
    name: "Vision Agent",
    role: "Medical Image & Visual Symptom Classifier",
    color: "#ec4899",
    description: "Processes dermatology photos, radiology scans, or rash images via Gemini Computer Vision adapter.",
    input_keys: ["image_artifacts"],
    output_keys: ["visual_findings", "anatomical_region", "image_quality_score"],
    model_tier: "Gemini 2.5 Flash (Multimodal Vision Adapter)",
    fallback_strategy: "Flag low image clarity and request user re-upload",
    rag_enabled: false
  },
  {
    id: "docs_agent",
    name: "Medical Docs Agent",
    role: "OCR & Document Parsing Engine",
    color: "#8b5cf6",
    description: "Parses PDFs, lab reports, discharge summaries, and prescriptions using layout-aware OCR adapters.",
    input_keys: ["document_artifacts"],
    output_keys: ["parsed_lab_values", "prescription_details", "icd_codes_found"],
    model_tier: "Gemini 2.5 Flash + OCR Feature Extractor",
    fallback_strategy: "Fallback to raw text tokenization & regex entity extraction",
    rag_enabled: false
  },
  {
    id: "timeline_agent",
    name: "Timeline Agent",
    role: "Longitudinal Clinical History Constructor",
    color: "#8FAF82",
    description: "Constructs chronological health events, previous treatments, surgeries, and drug response histories.",
    input_keys: ["parsed_lab_values", "structured_symptoms", "patient_id"],
    output_keys: ["clinical_timeline", "treatment_history", "chronic_conditions"],
    model_tier: "Gemini 2.5 Flash (Temporal Reasoning)",
    fallback_strategy: "Sort events chronologically by document dates",
    rag_enabled: false
  },
  {
    id: "evidence_agent",
    name: "Evidence Agent",
    role: "Medical RAG & Guidelines Retriever",
    color: "#06b6d4",
    description: "Queries ChromaDB vector store for clinical guidelines, PubMed literature, and specialist match matrices.",
    input_keys: ["chief_complaint", "clinical_timeline"],
    output_keys: ["retrieved_evidence", "clinical_guideline_citations", "vector_distance_scores"],
    model_tier: "Gemini Text Embeddings (004) + Vector Similarity",
    fallback_strategy: "Relax metadata filters or query hybrid BM25 + Vector ranking",
    rag_enabled: true
  },
  {
    id: "clinical_reasoning_agent",
    name: "Clinical Reasoning Agent",
    role: "Differential & Specialist Match Synthesizer",
    color: "#f59e0b",
    description: "Synthesizes symptoms, docs, and retrieved guidelines into candidate medical specialties (e.g., Rheumatology vs. Orthopedics).",
    input_keys: ["structured_symptoms", "clinical_timeline", "retrieved_evidence"],
    output_keys: ["differential_specialties", "reasoning_chain", "confidence_score"],
    model_tier: "Gemini 2.5 Pro (Complex Synthesis)",
    fallback_strategy: "Trigger Supervisor to ask clarifying questions if confidence < 0.6",
    rag_enabled: true
  },
  {
    id: "referral_agent",
    name: "Referral Agent",
    role: "Specialist Recommendation Engine",
    color: "#8FAF82",
    description: "Generates tailored recommendation summaries, question checklists for doctor visits, and recommended triage priority.",
    input_keys: ["differential_specialties", "reasoning_chain"],
    output_keys: ["recommended_specialist", "triage_urgency", "doctor_discussion_questions"],
    model_tier: "Gemini 2.5 Flash",
    fallback_strategy: "Default to General Internal Medicine triage",
    rag_enabled: false
  },
  {
    id: "safety_agent",
    name: "Safety Agent",
    role: "Red-Flag Triage & Emergency Override Guard",
    color: "#ef4444",
    description: "Evaluates immediate life-threatening red flags (chest pain, stroke symptoms, acute dyspnea). Can abort execution and trigger ER emergency response.",
    input_keys: ["raw_user_prompt", "structured_symptoms", "visual_findings"],
    output_keys: ["is_emergency", "red_flag_reasons", "emergency_instructions"],
    model_tier: "Deterministic Rule Engine + Gemini Safety Guard",
    fallback_strategy: "Failsafe: Any matching red-flag term forces EMERGENCY OVERRIDE",
    rag_enabled: false
  },
  {
    id: "care_plan_agent",
    name: "Care Plan Agent",
    role: "Actionable Patient Navigator",
    color: "#8FAF82",
    description: "Creates non-diagnostic, plain-language patient action plans, symptom logs, and preparation guides for consultations.",
    input_keys: ["recommended_specialist", "clinical_timeline"],
    output_keys: ["patient_action_plan", "symptom_tracking_log", "preparation_checklist"],
    model_tier: "Gemini 2.5 Flash (Patient Communication)",
    fallback_strategy: "Render standard pre-formatted specialist checklist",
    rag_enabled: false
  },
  {
    id: "followup_agent",
    name: "Follow-up Agent",
    role: "Continuous Monitoring & State Checkpointer",
    color: "#6366f1",
    description: "Schedules automated follow-up check-ins, tracks symptom evolution over time, and updates longitudinal PostgreSQL state.",
    input_keys: ["patient_action_plan", "session_id"],
    output_keys: ["followup_schedule", "state_checkpoint_id"],
    model_tier: "Postgres Checkpointer + Temporal Scheduler",
    fallback_strategy: "Log state snapshot to database asynchronously",
    rag_enabled: false
  }
];

export const PRODUCTION_FOLDER_TREE: FolderNode = {
  name: "carepath-backend",
  path: "carepath-backend",
  type: "folder",
  description: "Root backend project folder using FastAPI, LangGraph, Domain-Driven Design, and PostgreSQL.",
  children: [
    {
      name: "app",
      path: "app",
      type: "folder",
      description: "Main application module containing API routes, LangGraph agents, core configs, and database layer.",
      children: [
        {
          name: "api",
          path: "app/api",
          type: "folder",
          layer: "api",
          description: "REST & Streaming API Layer with FastAPI routers and middleware.",
          children: [
            {
              name: "v1",
              path: "app/api/v1",
              type: "folder",
              children: [
                {
                  name: "endpoints",
                  path: "app/api/v1/endpoints",
                  type: "folder",
                  children: [
                    {
                      name: "navigation.py",
                      path: "app/api/v1/endpoints/navigation.py",
                      type: "file",
                      layer: "api",
                      description: "Primary clinical intake and navigation workflow endpoints (Sync & Streaming SSE).",
                      codeSnippet: `from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sse_starlette.sse import EventSourceResponse
from app.schemas.navigation import IntakeRequest, NavigationResponse
from app.agents.orchestrator import LangGraphOrchestrator
from app.core.auth import get_current_user

router = APIRouter(prefix="/navigation", tags=["Navigation Workflow"])

@router.post("/intake", response_model=NavigationResponse)
async def submit_intake(
    request: IntakeRequest,
    orchestrator: LangGraphOrchestrator = Depends(),
    user = Depends(get_current_user)
):
    """Submits patient symptoms, images, and docs to LangGraph Multi-Agent System."""
    session_state = await orchestrator.run_workflow(request, user_id=user.id)
    return NavigationResponse.from_graph_state(session_state)

@router.get("/{session_id}/stream")
async def stream_agent_execution(session_id: str, orchestrator: LangGraphOrchestrator = Depends()):
    """Streams real-time step-by-step agent execution updates via Server-Sent Events (SSE)."""
    return EventSourceResponse(orchestrator.stream_session_events(session_id))`
                    },
                    {
                      name: "agents.py",
                      path: "app/api/v1/endpoints/agents.py",
                      type: "file",
                      layer: "api",
                      description: "Agent status, manual evaluation, and debugging endpoints for AI studio integration.",
                      codeSnippet: `from fastapi import APIRouter
from app.schemas.agents import AgentRegistrySchema
from app.agents.registry import get_all_agent_specs

router = APIRouter(prefix="/agents", tags=["Agent Registry"])

@router.get("/specs", response_model=AgentRegistrySchema)
async def list_agent_specs():
    """Returns specifications, metadata, and routing models for all 11 agents."""
    return get_all_agent_specs()`
                    },
                    {
                      name: "health.py",
                      path: "app/api/v1/endpoints/health.py",
                      type: "file",
                      layer: "api",
                      description: "Liveness and readiness health checks for Kubernetes / Cloud Run ingress.",
                      codeSnippet: `from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "CarePath AI Backend"}`
                    }
                  ]
                },
                {
                  name: "router.py",
                  path: "app/api/v1/router.py",
                  type: "file",
                  layer: "api",
                  description: "Combines all API routers for version 1.",
                  codeSnippet: `from fastapi import APIRouter
from app.api.v1.endpoints import navigation, agents, health

api_router = APIRouter()
api_router.include_router(navigation.router)
api_router.include_router(agents.router)
api_router.include_router(health.router)`
                }
              ]
            }
          ]
        },
        {
          name: "agents",
          path: "app/agents",
          type: "folder",
          layer: "agents",
          description: "LangGraph Multi-Agent Architecture definitions, supervisor router, state schema, and node handlers.",
          children: [
            {
              name: "state.py",
              path: "app/agents/state.py",
              type: "file",
              layer: "agents",
              description: "CarePathGlobalState Schema definition shared across all 11 agents.",
              codeSnippet: `from typing import TypedDict, List, Dict, Optional, Any
from pydantic import BaseModel, Field

class CarePathGlobalState(TypedDict):
    session_id: str
    patient_id: str
    raw_prompt: str
    uploaded_images: List[str]
    uploaded_docs: List[str]
    
    # Agent Outputs
    structured_symptoms: Optional[Dict[str, Any]]
    visual_findings: Optional[Dict[str, Any]]
    parsed_docs: Optional[Dict[str, Any]]
    clinical_timeline: Optional[List[Dict[str, Any]]]
    retrieved_evidence: Optional[List[Dict[str, Any]]]
    differential_specialties: Optional[List[Dict[str, Any]]]
    recommended_specialist: Optional[str]
    patient_action_plan: Optional[Dict[str, Any]]
    
    # Safety & Execution Controls
    is_emergency: bool
    emergency_reasons: List[str]
    confidence_score: float
    current_agent: str
    execution_history: List[Dict[str, Any]]
    retry_count: Dict[str, int]`
            },
            {
              name: "supervisor.py",
              path: "app/agents/supervisor.py",
              type: "file",
              layer: "agents",
              description: "Supervisor Agent determining dynamic conditional routing logic across nodes.",
              codeSnippet: `from app.agents.state import CarePathGlobalState

class SupervisorAgent:
    def route_next(self, state: CarePathGlobalState) -> str:
        # Emergency check override
        if state.get("is_emergency"):
            return "safety_agent"
            
        history = [e["agent_id"] for e in state.get("execution_history", [])]
        
        # Step 1: Safety check if not run
        if "safety_agent" not in history:
            return "safety_agent"
            
        # Step 2: Intake if symptoms not extracted
        if not state.get("structured_symptoms"):
            return "intake_agent"
            
        # Step 3: Vision if images present and not processed
        if state.get("uploaded_images") and not state.get("visual_findings"):
            return "vision_agent"
            
        # Step 4: Docs if PDFs present and not processed
        if state.get("uploaded_docs") and not state.get("parsed_docs"):
            return "docs_agent"
            
        # Step 5: Timeline construction
        if not state.get("clinical_timeline"):
            return "timeline_agent"
            
        # Step 6: Evidence retrieval (RAG)
        if not state.get("retrieved_evidence"):
            return "evidence_agent"
            
        # Step 7: Clinical Reasoning
        if not state.get("differential_specialties"):
            return "clinical_reasoning_agent"
            
        # Step 8: Referral & Care Plan
        if not state.get("recommended_specialist"):
            return "referral_agent"
            
        if not state.get("patient_action_plan"):
            return "care_plan_agent"
            
        return "followup_agent"`
            },
            {
              name: "graph.py",
              path: "app/agents/graph.py",
              type: "file",
              layer: "agents",
              description: "LangGraph StateGraph compiler connecting nodes, conditional edges, and Postgres checkpointers.",
              codeSnippet: `from langgraph.graph import StateGraph, END
from app.agents.state import CarePathGlobalState
from app.agents.supervisor import SupervisorAgent
from app.agents.nodes import (
    safety_node, intake_node, vision_node, docs_node,
    timeline_node, evidence_node, reasoning_node,
    referral_node, care_plan_node, followup_node
)

def build_carepath_graph():
    builder = StateGraph(CarePathGlobalState)
    
    # Add Nodes
    builder.add_node("safety_agent", safety_node)
    builder.add_node("intake_agent", intake_node)
    builder.add_node("vision_agent", vision_node)
    builder.add_node("docs_agent", docs_node)
    builder.add_node("timeline_agent", timeline_node)
    builder.add_node("evidence_agent", evidence_node)
    builder.add_node("clinical_reasoning_agent", reasoning_node)
    builder.add_node("referral_agent", referral_node)
    builder.add_node("care_plan_agent", care_plan_node)
    builder.add_node("followup_agent", followup_node)
    
    # Conditional Edges managed by Supervisor Router
    supervisor = SupervisorAgent()
    builder.set_conditional_entry_point(
        supervisor.route_next,
        {
            "safety_agent": "safety_agent",
            "intake_agent": "intake_agent",
            "vision_agent": "vision_agent",
            "docs_agent": "docs_agent"
        }
    )
    
    return builder.compile()`
            },
            {
              name: "nodes",
              path: "app/agents/nodes",
              type: "folder",
              children: [
                {
                  name: "safety_node.py",
                  path: "app/agents/nodes/safety_node.py",
                  type: "file",
                  layer: "agents",
                  description: "Safety Agent node implementation with strict regex and model red-flag classifier."
                },
                {
                  name: "intake_node.py",
                  path: "app/agents/nodes/intake_node.py",
                  type: "file",
                  layer: "agents",
                  description: "Intake Agent node extracting symptoms and severity scores."
                },
                {
                  name: "vision_node.py",
                  path: "app/agents/nodes/vision_node.py",
                  type: "file",
                  layer: "agents",
                  description: "Vision Agent node consuming AI team's computer vision service adapter."
                },
                {
                  name: "evidence_node.py",
                  path: "app/agents/nodes/evidence_node.py",
                  type: "file",
                  layer: "agents",
                  description: "Evidence Agent node executing ChromaDB similarity searches."
                }
              ]
            }
          ]
        },
        {
          name: "core",
          path: "app/core",
          type: "folder",
          layer: "core",
          description: "System configurations, security middleware, PHI redactor, logging, and JWT authentication.",
          children: [
            {
              name: "config.py",
              path: "app/core/config.py",
              type: "file",
              layer: "config",
              description: "Pydantic BaseSettings loading environment variables.",
              codeSnippet: `from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CarePath AI Backend"
    DATABASE_URL: str
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    JWT_SECRET: str
    GEMINI_API_KEY: str
    PHI_SALT: str

    class Config:
        env_file = ".env"`
            },
            {
              name: "security.py",
              path: "app/core/security.py",
              type: "file",
              layer: "core",
              description: "PHI Sanitizer / Redactor, AES-256 encryption utilities, and prompt injection filters.",
              codeSnippet: `import re

class PHIRedactor:
    """Sanitizes Personal Health Information before persisting or sending to LLMs."""
    PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "mrn": r"\bMRN[:\s]*[A-Z0-9]{6,10}\b"
    }

    def redact(self, text: str) -> str:
        clean = text
        for name, pattern in self.PATTERNS.items():
            clean = re.sub(pattern, f"[REDACTED_{name.upper()}]", clean)
        return clean`
            }
          ]
        },
        {
          name: "db",
          path: "app/db",
          type: "folder",
          layer: "db",
          description: "PostgreSQL database session management, SQLAlchemy / Drizzle models, and ChromaDB client initialization.",
          children: [
            {
              name: "postgres.py",
              path: "app/db/postgres.py",
              type: "file",
              layer: "db",
              description: "Async Engine & AsyncSession maker for PostgreSQL.",
              codeSnippet: `from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_size=20, max_overflow=10)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session`
            },
            {
              name: "chroma.py",
              path: "app/db/chroma.py",
              type: "file",
              layer: "db",
              description: "ChromaDB vector collection wrapper for medical guidelines RAG.",
              codeSnippet: `import chromadb
from app.core.config import settings

client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
evidence_collection = client.get_or_create_collection(name="carepath_evidence_v1")`
            },
            {
              name: "models.py",
              path: "app/db/models.py",
              type: "file",
              layer: "db",
              description: "SQLAlchemy ORM models (Patients, Encounters, AgentCheckpoints, AuditLogs).",
              codeSnippet: `from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class PatientEncounter(Base):
    __tablename__ = "patient_encounters"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    chief_complaint = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    state_json = Column(JSON)

class AgentCheckpoint(Base):
    __tablename__ = "agent_checkpoints"
    
    id = Column(String, primary_key=True)
    encounter_id = Column(String, ForeignKey("patient_encounters.id"))
    agent_id = Column(String, nullable=False)
    state_delta = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)`
            }
          ]
        },
        {
          name: "services",
          path: "app/services",
          type: "folder",
          layer: "services",
          description: "Integration service adapters interfacing with external AI team endpoints, OCR models, and notification queues.",
          children: [
            {
              name: "ai_models_adapter.py",
              path: "app/services/ai_models_adapter.py",
              type: "file",
              layer: "services",
              description: "Clean Adapter contract consuming the AI Team's vision, OCR, and NLP models.",
              codeSnippet: `from abc import ABC, abstractmethod
from typing import Dict, Any

class AIModelServiceAdapter(ABC):
    @abstractmethod
    async def analyze_medical_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Contract for AI Team's Vision Model Service."""
        pass

    @abstractmethod
    async def ocr_medical_document(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Contract for AI Team's Document OCR Service."""
        pass`
            }
          ]
        }
      ]
    },
    {
      name: "docker",
      path: "docker",
      type: "folder",
      description: "Docker Compose and Dockerfiles for FastAPI app, PostgreSQL, ChromaDB, and Redis.",
      children: [
        {
          name: "Dockerfile",
          path: "docker/Dockerfile",
          type: "file",
          description: "Multi-stage production Docker build for FastAPI and LangGraph runner."
        },
        {
          name: "docker-compose.yml",
          path: "docker/docker-compose.yml",
          type: "file",
          description: "Local development container topology."
        }
      ]
    },
    {
      name: "tests",
      path: "tests",
      type: "folder",
      layer: "tests",
      description: "Pytest suite for unit, integration, and agent graph evaluation.",
      children: [
        {
          name: "test_graph.py",
          path: "tests/test_graph.py",
          type: "file",
          layer: "tests",
          description: "Integration test evaluating dynamic conditional routing under emergency and routine cases."
        }
      ]
    }
  ]
};

export const BLUEPRINT_TOPICS: BlueprintTopic[] = [
  {
    id: "folder-structure",
    number: 1,
    title: "Production Folder Structure & Layered Clean Architecture",
    category: "core",
    summary: "Domain-driven layered architecture separating API transport, agent orchestration, core configuration, data access, and external AI team contracts.",
    keyDecisions: [
      "Strict separation between backend orchestration (FastAPI + LangGraph) and AI model inference (AI team microservices).",
      "Modular agent design under `app/agents/` allowing independent unit testing of node state transitions.",
      "Repository pattern in `app/db/` decoupling SQLAlchemy / ChromaDB calls from agent handlers."
    ],
    content: `CarePath AI adopts a Domain-Driven Clean Architecture designed for high maintainability and security in regulated healthcare environments.

### Architectural Principles
1. **API Transport Layer (\`app/api/\`)**: Exposes FastAPI endpoints (REST and Server-Sent Events). Zero business logic or database queries reside here; it validates Pydantic request models and delegates to orchestration services.
2. **Multi-Agent Orchestration Layer (\`app/agents/\`)**: Encapsulates LangGraph StateGraph definitions, Supervisor dynamic routing logic, and individual node handlers. Agents operate exclusively on immutable state snapshots (\`CarePathGlobalState\`).
3. **Core & Security Layer (\`app/core/\`)**: Contains the PHI Sanitizer, JWT authentication dependencies, environment configuration via Pydantic BaseSettings, and OpenTelemetry logging wrappers.
4. **Data Access Layer (\`app/db/\`)**: Manages async PostgreSQL sessions for relational state/checkpoints and ChromaDB clients for vector guideline retrieval.
5. **AI Team Integration Layer (\`app/services/\`)**: Provides Abstract Base Class (ABC) adapters to cleanly consume computer vision, OCR, and NLP models developed by the AI team without coupling.`
  },
  {
    id: "backend-architecture",
    number: 2,
    title: "Backend Core Architecture & System Topology",
    category: "core",
    summary: "Asynchronous, non-blocking FastAPI backend leveraging Python asyncio, Uvicorn worker pools, Redis state checkpointer, and PostgreSQL.",
    keyDecisions: [
      "Fully asynchronous event loop (`async/await`) across all HTTP routes, database drivers (`asyncpg`), and HTTP client calls (`httpx`).",
      "Redis checkpointer for ultra-low latency agent state resumption and crash recovery.",
      "Server-Sent Events (SSE) streaming for real-time visual feedback of agent node progress."
    ],
    diagramAscii: `
+---------------------------------------------------------------------------------+
|                                 CLIENT LAYER                                    |
|                   (React App / Web Dashboard / Mobile Web)                      |
+---------------------------------------------------------------------------------+
                                       |  HTTP POST / SSE Stream
                                       v
+---------------------------------------------------------------------------------+
|                            API GATEWAY & FASTAPI                                |
|  [ Auth / JWT Middleware ] -> [ PHI Redactor Filter ] -> [ Rate Limiter ]       |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       LANGGRAPH AGENT ORCHESTRATOR                              |
|                             (Supervisor Agent)                                  |
|   +-------------------------------------------------------------------------+   |
|   |  Safety -> Intake -> [Vision?] -> [Docs?] -> Timeline -> Evidence (RAG) |   |
|   |  -> Clinical Reasoning -> Referral -> Care Plan -> Follow-up            |   |
|   +-------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------+
          |                                   |                              |
          v                                   v                              v
+--------------------+              +--------------------+         +--------------------+
|  PostgreSQL 16 DB  |              |  ChromaDB Vectors  |         | AI Model Adapters  |
| (Checkpoints/PHI)  |              | (Medical RAG Data) |         | (Vision, OCR, NLP) |
+--------------------+              +--------------------+         +--------------------+
`,
    content: `The backend architecture is built around FastAPI and Uvicorn running on Python 3.12 with full async event loops.

### Key Architectural Characteristics
- **Concurrency Model**: Utilizes asyncpg for non-blocking PostgreSQL queries and httpx for async calls to external services.
- **State Checkpointing**: Every state transition in LangGraph is written to a Redis/Postgres checkpointer. If an agent node fails or times out, the workflow can resume from the last valid checkpoint without re-executing previous steps.
- **Real-Time Streaming**: Implements SSE (\`sse-starlette\`) to emit structured JSON events as each agent finishes its pass. This allows the React frontend to show live status indicators (e.g., "Medical Docs Agent: Parsed 12 Lab Parameters").`
  },
  {
    id: "langgraph-architecture",
    number: 3,
    title: "LangGraph Multi-Agent Architecture & Dynamic Routing",
    category: "agents",
    summary: "Dynamic StateGraph workflow with 11 specialized agents, supervisor router, conditional edges, and safety short-circuiting.",
    keyDecisions: [
      "Dynamic routing over static DAGs: The Supervisor agent inspects available state keys to determine the next agent node.",
      "Safety First Short-Circuit: Safety Agent runs first and can immediately abort workflow if emergency red flags are detected.",
      "Conditional Node Skipping: Vision and Docs agents are dynamically bypassed if no image or PDF artifacts exist in the request payload."
    ],
    content: `The system uses LangGraph to construct a stateful, multi-agent computational graph where execution is dynamic rather than linear.

### The 11 Agents Matrix
1. **Supervisor Agent**: The brain of the graph. Evaluates \`CarePathGlobalState\` and determines the next node or termination state.
2. **Safety Agent**: Red-flag triaging (chest pain, stroke signs, severe dyspnea). Has authority to immediately trigger emergency mode.
3. **Intake Agent**: Extracts structured symptoms, onset dates, severity (1-10), and aggravating/relieving factors.
4. **Vision Agent**: Multimodal visual analysis for skin lesions, rashes, swelling, or anatomical photos.
5. **Medical Docs Agent**: OCR parsing for lab results (blood panels, metabolic panels), discharge reports, and prescriptions.
6. **Timeline Agent**: Constructs chronological longitudinal patient trajectory.
7. **Evidence Agent (RAG)**: Executes vector queries against ChromaDB to find medical practice guidelines and specialist referral criteria.
8. **Clinical Reasoning Agent**: Synthesizes symptoms, labs, and evidence to produce candidate specialties with rationale.
9. **Referral Agent**: Formulates clear referral recommendations and specific questions the patient should ask their physician.
10. **Care Plan Agent**: Generates actionable, non-diagnostic patient preparation plans and symptom trackers.
11. **Follow-up Agent**: Schedules automated check-ins and updates longitudinal patient history in PostgreSQL.`
  },
  {
    id: "agent-communication",
    number: 4,
    title: "Agent Communication & Shared Global State Schema",
    category: "agents",
    summary: "Explicit shared state dictionary (`CarePathGlobalState`) passed immutably between graph nodes with strict key typing.",
    keyDecisions: [
      "No direct agent-to-agent REST calls: Communication occurs strictly through reads and updates to `CarePathGlobalState`.",
      "Append-only execution history for auditability: Each agent appends its decision log, execution time, and confidence score.",
      "Confidence-weighted updates: Lower confidence outputs (<0.65) trigger clarification loops instead of proceeding."
    ],
    content: `Agents communicate exclusively by modifying the shared \`CarePathGlobalState\` object passed through LangGraph nodes.

### Shared State Schema Structure
\`\`\`python
class CarePathGlobalState(TypedDict):
    session_id: str
    patient_id: str
    raw_prompt: str
    uploaded_images: List[str]
    uploaded_docs: List[str]
    
    # Artifact Outputs
    structured_symptoms: Optional[Dict[str, Any]]
    visual_findings: Optional[Dict[str, Any]]
    parsed_docs: Optional[Dict[str, Any]]
    clinical_timeline: Optional[List[Dict[str, Any]]]
    retrieved_evidence: Optional[List[Dict[str, Any]]]
    differential_specialties: Optional[List[Dict[str, Any]]]
    recommended_specialist: Optional[str]
    patient_action_plan: Optional[Dict[str, Any]]
    
    # Metadata & Controls
    is_emergency: bool
    emergency_reasons: List[str]
    confidence_score: float
    current_agent: str
    execution_history: List[Dict[str, Any]]
\`\`\``
  },
  {
    id: "api-design",
    number: 5,
    title: "API Contract & REST/SSE Endpoint Design",
    category: "core",
    summary: "Production REST endpoints with OpenAPI validation schemas, SSE streaming, and structured HTTP error responses.",
    keyDecisions: [
      "Dual REST / SSE pattern: Standard `POST /api/v1/navigation/intake` for sync responses and `GET /api/v1/navigation/{session_id}/stream` for live progression updates.",
      "Strict Pydantic payload validation with clear custom error messages for malformed input.",
      "Idempotency keys on workflow submissions to prevent duplicate execution triggers."
    ],
    content: `FastAPI exposes clean RESTful endpoints documented via OpenAPI 3.1.

### Primary API Routes
- \`POST /api/v1/navigation/intake\`: Accepts text prompt, image base64 strings, and doc attachments.
- \`GET /api/v1/navigation/{session_id}/stream\`: SSE stream yielding agent progress ticks (\`agent_started\`, \`agent_completed\`, \`emergency_override\`).
- \`GET /api/v1/navigation/{session_id}/state\`: Retrieves latest graph state checkpoint from PostgreSQL.
- \`POST /api/v1/security/redact\`: Test sandbox for PHI text sanitization.
- \`GET /api/v1/agents/specs\`: Introspection endpoint exposing metadata for all 11 agents.`
  },
  {
    id: "database-design",
    number: 6,
    title: "Database Interaction & Hybrid Relational + Vector Storage",
    category: "data",
    summary: "PostgreSQL 16 for structured entities, state checkpoints, and audit logs; ChromaDB for medical guidelines vector search.",
    keyDecisions: [
      "PostgreSQL for ACID compliance, relational foreign keys, and longitudinal state persistence.",
      "ChromaDB collection `carepath_evidence_v1` using 768-dimensional medical embeddings for RAG retrieval.",
      "Separate audit tables for PHI compliance logging with immutability guarantees."
    ],
    content: `CarePath AI utilizes a hybrid data architecture combining relational storage and vector indexing.

### PostgreSQL Schema Tables
1. **\`patients\`**: Hashed patient identifiers, consent flags, encrypted demographic metadata.
2. **\`patient_encounters\`**: Clinical intake sessions, chief complaint, triage urgency, and state snapshot JSON.
3. **\`agent_checkpoints\`**: LangGraph state snapshots captured after every node execution for fault tolerance.
4. **\`audit_logs\`**: Immutable log of every access to PHI or agent decision trigger.

### ChromaDB Vector Collection Schema
- **Collection Name**: \`carepath_evidence_v1\`
- **Embedding Model**: Gemini Text Embeddings (\`text-embedding-004\`, 768-dim)
- **Metadata Fields**: \`specialty\`, \`guideline_source\`, \`publication_year\`, \`evidence_grade\``
  },
  {
    id: "auth-flow",
    number: 7,
    title: "Authentication, Authorization & Role-Based Access Control",
    category: "security",
    summary: "OAuth2 with Password/Bearer JWT tokens, tenant isolation, fine-grained RBAC, and HIPAA session expiration.",
    keyDecisions: [
      "Short-lived JWT access tokens (15 mins) + HTTP-only encrypted refresh cookies.",
      "Role-Based Access Control (RBAC): `PATIENT`, `CLINICIAN`, `SYSTEM_ADMIN`, `AGENT_RUNNER`.",
      "Strict row-level security (RLS) policies isolating patient encounters by `patient_id`."
    ],
    content: `Authentication is enforced at the FastAPI middleware layer before requests reach router code.

### Security Token Specification
- Algorithm: \`HS256\` / \`RS256\`
- Payload: \`sub\` (patient_id), \`role\`, \`tenant_id\`, \`exp\`
- Token Revocation: Redis blocklist for logged-out or compromised sessions.`
  },
  {
    id: "request-lifecycle",
    number: 8,
    title: "End-to-End Request Lifecycle & Execution Trace",
    category: "core",
    summary: "Trace of a user request from client submit through Auth, PHI redaction, LangGraph routing, DB state persistence, and SSE notification.",
    keyDecisions: [
      "Synchronous fast-path for emergency checks (<50ms).",
      "Asynchronous background task processing for heavy OCR / Computer Vision pipelines.",
      "Immediate state checkpointing after each node transition."
    ],
    content: `### Execution Sequence
1. **Client Request**: React frontend sends intake payload to \`POST /api/v1/navigation/intake\`.
2. **Middleware**: Auth Middleware validates JWT; PHI Redactor sanitizes raw text prompt.
3. **LangGraph Initialization**: Supervisor creates initial \`CarePathGlobalState\` and saves initial checkpoint in PostgreSQL.
4. **Safety Node**: Evaluates red flags. If critical emergency is detected, state is updated to \`is_emergency=True\` and workflow aborts immediately with 911 instructions.
5. **Intake Node**: Extracts structured symptoms.
6. **Vision / Docs Nodes**: Executed dynamically if image or PDF attachments exist.
7. **Timeline & Evidence Nodes**: Constructs clinical trajectory and queries ChromaDB for guidelines.
8. **Reasoning & Referral Nodes**: Formulates specialist recommendation and discussion checklist.
9. **Care Plan & Follow-up Nodes**: Generates plain-language action guide and schedules check-in snapshot in PostgreSQL.
10. **Response**: Final summary returned to client; client receives SSE notifications at each step.`
  },
  {
    id: "error-handling",
    number: 9,
    title: "Error Handling & Circuit Breaker Resilience",
    category: "core",
    summary: "Comprehensive fault tolerance using tenacity retries, agent node fallbacks, state rollbacks, and circuit breakers.",
    keyDecisions: [
      "Exponential backoff with jitter on external model API calls.",
      "Agent Fallback Nodes: If Vision Agent fails, workflow continues with text-based intake rather than crashing.",
      "Global FastAPI Exception Handlers returning RFC 7807 Problem Details JSON."
    ],
    content: `Healthcare navigation must never crash silently or leave patients in an undefined state.

### Resilience Patterns
- **API Retries**: Exponential backoff retry handler (\`tenacity\` library) for transient Gemini API rate limits (HTTP 429 / 503).
- **Graceful Node Degradation**: If an image fail to parse, the Vision Agent logs a warning, sets \`visual_findings = {"error": "Image unclear"}\`, and yields control back to Supervisor to proceed with text-based triage.
- **Circuit Breaker**: Microservice calls to the AI team's adapters wrap calls in a circuit breaker to prevent cascading failures.`
  },
  {
    id: "logging-strategy",
    number: 10,
    title: "Structured Logging, OpenTelemetry & Agent Audit Trails",
    category: "core",
    summary: "Structured JSON logs, correlation IDs per session, OpenTelemetry tracing, and PHI-redacted log sinks.",
    keyDecisions: [
      "Structured JSON logs (`structlog`) for automated ingestion into Grafana Loki / Cloud Logging.",
      "Unique `trace_id` and `session_id` injected into all log contexts.",
      "Automatic PHI redaction filter attached to standard log handlers to prevent accidental PHI leaks."
    ],
    content: `All backend components write structured JSON logs with context attributes.

### Sample JSON Log Event
\`\`\`json
{
  "timestamp": "2026-08-05T08:12:00.123Z",
  "level": "INFO",
  "logger": "app.agents.supervisor",
  "trace_id": "tr_8a91b2c3",
  "session_id": "sess_f47a11",
  "agent_id": "supervisor_agent",
  "event": "ROUTE_DECISION",
  "chosen_next_node": "evidence_agent",
  "reason": "Structured symptoms present; guidelines retrieval required",
  "execution_time_ms": 14.2
}
\`\`\``
  },
  {
    id: "security-strategy",
    number: 11,
    title: "Security Architecture, PHI Protection & Prompt Injection Defense",
    category: "security",
    summary: "Defense-in-depth security including AES-256 field encryption, automatic PHI sanitization, TLS 1.3, and LLM guardrails.",
    keyDecisions: [
      "Automatic PHI Redaction Filter before sending patient strings to external LLMs.",
      "AES-256-GCM encryption at rest for database columns containing sensitive medical text.",
      "Strict input sanitization preventing prompt injection attacks on agent nodes."
    ],
    content: `Security and patient privacy are foundational to CarePath AI.

### Security Layers
1. **Data in Transit**: TLS 1.3 required on all ingress and egress traffic.
2. **Data at Rest**: PostgreSQL database encrypted with AES-256-GCM; database connection strings managed via GCP Secret Manager / Vault.
3. **PHI Masking**: Names, SSNs, phone numbers, and email addresses are automatically scrubbed by \`PHIRedactor\` before prompts are passed to Gemini models.
4. **Prompt Injection Guard**: User input is enclosed in strict XML boundaries (\`<user_input>...\</user_input>\`) with system instruction overrides prohibited.`
  },
  {
    id: "scalability",
    number: 12,
    title: "Future Scalability, Caching & Microservice Migration",
    category: "devops",
    summary: "Horizontal scaling strategy with Stateless FastAPI containers, Redis state caching, Celery/NATS task queues, and read-replicas.",
    keyDecisions: [
      "Stateless FastAPI application layer allowing auto-scaling from 1 to 100+ Cloud Run / Kubernetes pods.",
      "Redis for state caching, session locks, and rate limiting.",
      "PostgreSQL read-replicas for heavy clinical history queries and analytical workloads."
    ],
    content: `CarePath AI is designed for horizontal scaling under heavy patient intake volume.

### Scaling Milestones
- **Phase 1 (Sprint 0 - 2)**: Single-region Docker container deployment with connection pooling.
- **Phase 2 (Production Launch)**: Kubernetes (GKE / Cloud Run) with Horizontal Pod Autoscaler (HPA) based on CPU and HTTP concurrency metrics.
- **Phase 3 (Enterprise Multi-Region)**: PostgreSQL primary-replica architecture across multiple cloud regions with Redis cluster.`
  },
  {
    id: "ai-team-integration",
    number: 13,
    title: "Integration Points with AI Team (Model Interfaces & Adapters)",
    category: "devops",
    summary: "Strict interface contracts (Pydantic / Abstract Base Classes) decoupling backend orchestration from AI team model releases.",
    keyDecisions: [
      "AI team delivers model endpoints behind gRPC / REST contracts or Python package interfaces.",
      "Mock adapters provided in `app/services/` so backend team can test full graph without waiting for model deployment.",
      "Versioned API contracts (`v1/vision`, `v1/ocr`, `v1/nlp`) with schema compatibility tests."
    ],
    content: `To enable parallel development with the AI team, clear interface contracts are established.

### Contract Definition Example
\`\`\`python
class VisionModelInput(BaseModel):
    image_bytes_base64: str
    anatomical_context: Optional[str] = None

class VisionModelOutput(BaseModel):
    visual_findings: str
    confidence: float
    detected_features: List[str]
\`\`\``
  },
  {
    id: "frontend-integration",
    number: 14,
    title: "Integration Points with Frontend Team (OpenAPI & SSE)",
    category: "devops",
    summary: "Auto-generated OpenAPI client SDKs, SSE subscription hooks, optimism rendering, and structured error payloads.",
    keyDecisions: [
      "Auto-generated TypeScript types via OpenAPI schema (`openapi-typescript`).",
      "EventSource SSE listener utility for React custom hook `useCarePathStream`.",
      "Standardized HTTP error bodies with clear action codes for user UI guidance."
    ],
    content: `The frontend consumes the backend through auto-generated OpenAPI TypeScript definitions.

### React Integration Hook Example
\`\`\`typescript
export function useCarePathNavigation(sessionId: string) {
  const [steps, setSteps] = useState<SimulationStep[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource(\`/api/v1/navigation/\${sessionId}/stream\`);
    eventSource.onmessage = (event) => {
      const step = JSON.parse(event.data);
      setSteps((prev) => [...prev, step]);
    };
    return () => eventSource.close();
  }, [sessionId]);
  
  return { steps };
}
\`\`\``
  },
  {
    id: "deployment-architecture",
    number: 15,
    title: "Deployment Architecture, Docker & CI/CD Strategy",
    category: "devops",
    summary: "Containerized deployment using Docker Compose, Kubernetes/Cloud Run, GitHub Actions CI/CD pipelines, and database migrations.",
    keyDecisions: [
      "Multi-stage Dockerfile optimizing image size (<200MB) with non-root security user.",
      "Alembic database migrations running automatically during release deployment.",
      "Automated Pytest and Black/Ruff linting in CI/CD before container image push."
    ],
    diagramAscii: `
[ Developer Git Push ] -> [ GitHub Actions CI/CD ]
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
   [ Run Pytest & Lint ]             [ Build Docker Image ]
              |                                 |
              v                                 v
   [ DB Migration Check ]            [ Push to Artifact Registry ]
                                                |
                                                v
                                     [ Deploy to Cloud Run / GKE ]
`,
    content: `The deployment setup relies on containerized microservices managed via Docker.

### Multi-Stage Dockerfile Strategy
1. **Builder Stage**: Installs poetry/pip dependencies and compiles wheels.
2. **Runner Stage**: Minimal distroless or Debian slim base image running Uvicorn with a non-root system user for security compliance.`
  }
];

export const API_ENDPOINTS: ApiEndpointSpec[] = [
  {
    method: "POST",
    path: "/api/v1/navigation/intake",
    summary: "Submit Clinical Intake Payload",
    description: "Initiates the multi-agent CarePath AI navigation workflow with symptoms, images, and document attachments.",
    tags: ["Navigation Workflow"],
    requestBody: {
      patient_id: "pat_994182",
      chief_complaint: "I have had severe swelling and pain in both knees for 3 weeks, plus morning stiffness lasting over an hour.",
      uploaded_images: ["data:image/jpeg;base64,..."],
      uploaded_docs: ["data:application/pdf;base64,..."]
    },
    responses: {
      200: {
        session_id: "sess_x8f91a2",
        status: "PROCESSING_OR_COMPLETED",
        recommended_specialist: "Rheumatologist",
        triage_urgency: "SPECIALIST_EVALUATION_RECOMMENDED",
        steps_executed: 10,
        total_time_ms: 1650
      },
      400: { detail: "Invalid input payload or unsupported document format" },
      500: { detail: "Internal agent execution error - fallback triggered" }
    }
  },
  {
    method: "GET",
    path: "/api/v1/navigation/{session_id}/stream",
    summary: "Stream Real-Time Agent Execution Ticks (SSE)",
    description: "Establishes a Server-Sent Events stream delivering step-by-step agent decisions, confidence metrics, and state deltas.",
    tags: ["Navigation Workflow"],
    isStream: true,
    responses: {
      200: "text/event-stream (Yields json events for each agent step)"
    }
  },
  {
    method: "POST",
    path: "/api/v1/security/redact",
    summary: "Test PHI Text Sanitization",
    description: "Submits a text block to the PHI Redactor utility to test SSN, Phone, Email, and MRN masking rules.",
    tags: ["Security & PHI"],
    requestBody: {
      text: "Patient John Doe (SSN: 123-45-6789, DOB: 05/12/1980) called from 555-123-4567 reporting rash."
    },
    responses: {
      200: {
        original_length: 98,
        redacted_length: 104,
        redacted_text: "Patient John Doe (SSN: [REDACTED_SSN], DOB: [REDACTED_DOB]) called from [REDACTED_PHONE] reporting rash.",
        phi_detected: true,
        audit_hash: "sha256_b7a91c"
      }
    }
  },
  {
    method: "GET",
    path: "/api/v1/agents/specs",
    summary: "Fetch Specifications for All 11 Agents",
    description: "Returns metadata, input/output keys, model tiers, and fallback strategies for all 11 system agents.",
    tags: ["Agent Registry"],
    responses: {
      200: {
        total_agents: 11,
        agents: "Array<AgentSpec>"
      }
    }
  },
  {
    method: "GET",
    path: "/api/v1/health",
    summary: "Service Health Check",
    description: "Checks health status of FastAPI, PostgreSQL pool, ChromaDB vector store, and Redis checkpointer.",
    tags: ["System"],
    responses: {
      200: {
        status: "healthy",
        service: "CarePath AI Core Orchestrator API",
        components: {
          fastapi_gateway: "UP",
          postgresql_primary: "CONNECTED",
          chromadb_cluster: "CONNECTED"
        }
      }
    }
  }
];
