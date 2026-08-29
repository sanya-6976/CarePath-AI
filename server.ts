import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

const app = express();
const PORT = 3000;

app.use(express.json());

// --- Mock API endpoints for CarePath AI Backend Simulator ---

// Healthcheck
app.get("/api/v1/health", (req, res) => {
  res.json({
    status: "healthy",
    service: "CarePath AI Core Orchestrator API",
    version: "1.0.0-sprint0",
    environment: process.env.NODE_ENV || "development",
    timestamp: new Date().toISOString(),
    components: {
      fastapi_gateway: "UP",
      langgraph_orchestrator: "UP",
      postgresql_primary: "CONNECTED (Pool Size: 20)",
      chromadb_cluster: "CONNECTED (Collections: carepath_evidence_v1)",
      redis_checkpointer: "CONNECTED",
      security_phi_redactor: "ACTIVE"
    }
  });
});

// Agents List Endpoint
app.get("/api/v1/agents/specs", (req, res) => {
  res.json({
    total_agents: 11,
    agents: [
      {
        id: "supervisor_agent",
        name: "Supervisor Agent",
        role: "Dynamic Graph Router & Task Allocator",
        color: "#6366f1",
        description: "Evaluates current global graph state, incoming artifacts, and execution metrics to dynamically compute next agent nodes or terminate workflow.",
        input_keys: ["patient_symptoms", "uploaded_files", "agent_outputs", "emergency_flags"],
        output_keys: ["next_agent", "execution_plan", "is_complete"]
      },
      {
        id: "intake_agent",
        name: "Intake Agent",
        role: "Symptom & History Harvester",
        color: "#3b82f6",
        description: "Extracts structured clinical symptoms, duration, severity scale (1-10), aggravating factors, and demographic context.",
        input_keys: ["raw_user_prompt", "conversation_history"],
        output_keys: ["structured_symptoms", "chief_complaint", "severity_score"]
      },
      {
        id: "vision_agent",
        name: "Vision Agent",
        role: "Medical Image & Visual Symptom Classifier",
        color: "#ec4899",
        description: "Processes dermatology photos, radiology scans, or rash images via Gemini Computer Vision adapter.",
        input_keys: ["image_artifacts"],
        output_keys: ["visual_findings", "anatomical_region", "image_quality_score"]
      },
      {
        id: "docs_agent",
        name: "Medical Docs Agent",
        role: "OCR & Document Parsing Engine",
        color: "#8b5cf6",
        description: "Parses PDFs, lab reports, discharge summaries, and prescriptions using layout-aware OCR adapters.",
        input_keys: ["document_artifacts"],
        output_keys: ["parsed_lab_values", "prescription_details", "icd_codes_found"]
      },
      {
        id: "timeline_agent",
        name: "Timeline Agent",
        role: "Longitudinal Clinical History Constructor",
        color: "#10b981",
        description: "Constructs chronological health events, previous treatments, surgeries, and drug response histories.",
        input_keys: ["parsed_lab_values", "structured_symptoms", "patient_id"],
        output_keys: ["clinical_timeline", "treatment_history", "chronic_conditions"]
      },
      {
        id: "evidence_agent",
        name: "Evidence Agent",
        role: "Medical RAG & Guidelines Retriever",
        color: "#06b6d4",
        description: "Queries ChromaDB vector store for clinical guidelines, PubMed literature, and specialist match matrices.",
        input_keys: ["chief_complaint", "clinical_timeline"],
        output_keys: ["retrieved_evidence", "clinical_guideline_citations", "vector_distance_scores"]
      },
      {
        id: "clinical_reasoning_agent",
        name: "Clinical Reasoning Agent",
        role: "Differential & Specialist Match Synthesizer",
        color: "#f59e0b",
        description: "Synthesizes symptoms, docs, and retrieved guidelines into candidate medical specialties (e.g., Rheumatology vs. Orthopedics).",
        input_keys: ["structured_symptoms", "clinical_timeline", "retrieved_evidence"],
        output_keys: ["differential_specialties", "reasoning_chain", "confidence_score"]
      },
      {
        id: "referral_agent",
        name: "Referral Agent",
        role: "Specialist Recommendation Engine",
        color: "#10b981",
        description: "Generates tailored recommendation summaries, question checklists for doctor visits, and recommended triage priority.",
        input_keys: ["differential_specialties", "reasoning_chain"],
        output_keys: ["recommended_specialist", "triage_urgency", "doctor_discussion_questions"]
      },
      {
        id: "safety_agent",
        name: "Safety Agent",
        role: "Red-Flag Triage & Emergency Override Guard",
        color: "#ef4444",
        description: "Evaluates immediate life-threatening red flags (chest pain, stroke symptoms, acute dyspnea). Can abort execution and trigger ER emergency response.",
        input_keys: ["raw_user_prompt", "structured_symptoms", "visual_findings"],
        output_keys: ["is_emergency", "red_flag_reasons", "emergency_instructions"]
      },
      {
        id: "care_plan_agent",
        name: "Care Plan Agent",
        role: "Actionable Patient Navigator",
        color: "#84cc16",
        description: "Creates non-diagnostic, plain-language patient action plans, symptom logs, and preparation guides for consultations.",
        input_keys: ["recommended_specialist", "clinical_timeline"],
        output_keys: ["patient_action_plan", "symptom_tracking_log", "preparation_checklist"]
      },
      {
        id: "followup_agent",
        name: "Follow-up Agent",
        role: "Continuous Monitoring & State Checkpointer",
        color: "#6366f1",
        description: "Schedules automated follow-up check-ins, tracks symptom evolution over time, and updates longitudinal PostgreSQL state.",
        input_keys: ["patient_action_plan", "session_id"],
        output_keys: ["followup_schedule", "state_checkpoint_id"]
      }
    ]
  });
});

// PHI Redactor Test Endpoint
app.post("/api/v1/security/redact", (req, res) => {
  const { text } = req.body;
  if (!text) {
    return res.status(400).json({ error: "Text field required" });
  }

  // Regex rules for PHI sanitization testing
  const ssnPattern = /\b\d{3}-\d{2}-\d{4}\b/g;
  const phonePattern = /\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g;
  const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const mrnPattern = /\bMRN[:\s]*[A-Z0-9]{6,10}\b/gi;
  const dobPattern = /\bDOB[:\s]*\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}\b/gi;

  let redacted = text
    .replace(ssnPattern, "[REDACTED_SSN]")
    .replace(phonePattern, "[REDACTED_PHONE]")
    .replace(emailPattern, "[REDACTED_EMAIL]")
    .replace(mrnPattern, "MRN: [REDACTED_MRN]")
    .replace(dobPattern, "DOB: [REDACTED_DOB]");

  res.json({
    original_length: text.length,
    redacted_length: redacted.length,
    redacted_text: redacted,
    phi_detected: text !== redacted,
    audit_hash: "sha256_" + Math.random().toString(36).substring(2, 10)
  });
});

// LangGraph Execution Simulator
app.post("/api/v1/simulation/run", (req, res) => {
  const { prompt, has_image, has_document } = req.body;
  
  const lower = (prompt || "").toLowerCase();
  const isEmergency = lower.includes("chest pain") || lower.includes("shortness of breath") || lower.includes("stroke") || lower.includes("unconscious") || lower.includes("emergency");
  
  const executionSteps = [];

  // Step 1: Safety Agent First Check
  executionSteps.push({
    step: 1,
    agent_id: "safety_agent",
    agent_name: "Safety Agent",
    status: isEmergency ? "EMERGENCY_TRIGGERED" : "PASSED",
    decision: isEmergency ? "ABORT_WORKFLOW_TRIGGER_EMERGENCY" : "PROCEED_TO_INTAKE",
    confidence: 0.99,
    timestamp_ms: 45,
    state_delta: { is_emergency: isEmergency, red_flags: isEmergency ? ["Acute chest distress / emergency keywords detected"] : [] }
  });

  if (isEmergency) {
    return res.json({
      session_id: "sess_" + Math.random().toString(36).substring(2, 9),
      workflow_status: "ABORTED_SAFETY_EMERGENCY",
      total_time_ms: 52,
      steps: executionSteps,
      summary: {
        triage_urgency: "CRITICAL_EMERGENCY_911",
        recommendation: "Immediate emergency evaluation required. Call 911 or visit the nearest Emergency Department immediately."
      }
    });
  }

  // Step 2: Supervisor -> Intake Agent
  executionSteps.push({
    step: 2,
    agent_id: "intake_agent",
    agent_name: "Intake Agent",
    status: "SUCCESS",
    decision: "SYMPTOMS_EXTRACTED",
    confidence: 0.94,
    timestamp_ms: 180,
    state_delta: {
      chief_complaint: prompt || "Persistent joint pain and fatigue",
      severity_score: 6,
      duration: "3 weeks"
    }
  });

  // Step 3: Conditional Branching
  let stepIndex = 3;

  if (has_image) {
    executionSteps.push({
      step: stepIndex++,
      agent_id: "vision_agent",
      agent_name: "Vision Agent",
      status: "SUCCESS",
      decision: "IMAGE_CLASSIFIED",
      confidence: 0.91,
      timestamp_ms: 420,
      state_delta: { visual_findings: "Erythematous papular rash with well-demarcated borders", anatomical_region: "Right knee and shin" }
    });
  }

  if (has_document) {
    executionSteps.push({
      step: stepIndex++,
      agent_id: "docs_agent",
      agent_name: "Medical Docs Agent",
      status: "SUCCESS",
      decision: "DOCUMENTS_PARSED",
      confidence: 0.96,
      timestamp_ms: 610,
      state_delta: { parsed_labs: { ANA: "Positive (1:320)", ESR: "42 mm/hr (Elevated)" }, prescriptions: ["Ibuprofen 400mg TID"] }
    });
  }

  // Step Timeline Agent
  executionSteps.push({
    step: stepIndex++,
    agent_id: "timeline_agent",
    agent_name: "Timeline Agent",
    status: "SUCCESS",
    decision: "TIMELINE_CONSTRUCTED",
    confidence: 0.93,
    timestamp_ms: 780,
    state_delta: { timeline_events_count: 3, longitudinal_trend: "Progressive inflammatory symptom onset" }
  });

  // Step Evidence Agent (RAG)
  executionSteps.push({
    step: stepIndex++,
    agent_id: "evidence_agent",
    agent_name: "Evidence Agent",
    status: "SUCCESS",
    decision: "RETRIEVED_CHROMA_GUIDELINES",
    confidence: 0.89,
    timestamp_ms: 950,
    state_delta: { RAG_citations: ["ACR Clinical Practice Guidelines 2024", "UpToDate: Inflammatory Arthropathies"], distance_score: 0.18 }
  });

  // Step Clinical Reasoning Agent
  executionSteps.push({
    step: stepIndex++,
    agent_id: "clinical_reasoning_agent",
    agent_name: "Clinical Reasoning Agent",
    status: "SUCCESS",
    decision: "SYNTHESIZED_DIFFERENTIAL_SPECIALTIES",
    confidence: 0.88,
    timestamp_ms: 1210,
    state_delta: { primary_specialty: "Rheumatology", secondary_specialty: "Dermatology", reasoning: "Constellation of elevated inflammatory markers, ANA positivity, and joint stiffness strongly aligns with autoimmune rheumatological etiology." }
  });

  // Step Referral Agent
  executionSteps.push({
    step: stepIndex++,
    agent_id: "referral_agent",
    agent_name: "Referral Agent",
    status: "SUCCESS",
    decision: "SPECIALIST_RECOMMENDED",
    confidence: 0.95,
    timestamp_ms: 1380,
    state_delta: { recommended_specialist: "Rheumatologist", recommended_timeframe: "Within 1-2 weeks", questions_for_doctor: ["Should we perform anti-dsDNA or ENA panel testing?", "Is a skin biopsy warranted if rash persists?"] }
  });

  // Step Care Plan Agent
  executionSteps.push({
    step: stepIndex++,
    agent_id: "care_plan_agent",
    agent_name: "Care Plan Agent",
    status: "SUCCESS",
    decision: "CARE_PLAN_GENERATED",
    confidence: 0.97,
    timestamp_ms: 1540,
    state_delta: { action_plan: "Log morning stiffness duration daily, prepare lab results for appointment, monitor skin lesions." }
  });

  // Step Followup Agent
  executionSteps.push({
    step: stepIndex++,
    agent_id: "followup_agent",
    agent_name: "Follow-up Agent",
    status: "SUCCESS",
    decision: "CHECKPOINT_SAVED_POSTGRES",
    confidence: 0.99,
    timestamp_ms: 1650,
    state_delta: { followup_scheduled: "In 72 hours via automated SMS/app prompt", postgres_checkpoint_id: "ckpt_8f93a110" }
  });

  res.json({
    session_id: "sess_" + Math.random().toString(36).substring(2, 9),
    workflow_status: "COMPLETED",
    total_time_ms: 1650,
    steps: executionSteps,
    summary: {
      triage_urgency: "MODERATE_SPECIALIST_EVALUATION",
      recommended_specialist: "Rheumatologist (Secondary: Dermatologist)",
      confidence: 0.92,
      rag_evidence_sources: 2
    }
  });
});

// Vite Middleware Integration
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`CarePath AI Backend Orchestrator listening on http://0.0.0.0:${PORT}`);
  });
}

startServer();
