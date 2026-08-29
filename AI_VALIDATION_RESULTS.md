# AI Validation Results

## Status: not clinically validated

The active `backend.app.agents.graph` imports node implementations from `src.agents`. Code inspection shows heuristic/deterministic fallback behavior in active Intake, Vision, OCR/Docs, Evidence, Clinical Reasoning, Referral, Care Plan, Follow-up, and Safety paths. These components are **implemented but mocked/fallback-based** unless a separately tested live integration replaces them.

- **Gemini:** key presence was not reported or exercised; live response, error, timeout, rate-limit, malformed-response, and safety testing are blocked.
- **ChromaDB/RAG:** code exists, but retrieval was not executed. Do not claim WHO/CDC/PubMed evidence retrieval.
- **Vision/OCR:** no technical corpus or clinical-quality measurement ran. Do not claim medical-image or medical-grade OCR accuracy.
- **Clinical reasoning / safety:** deterministic code exists and longitudinal fields are wired; no clinical validation or adversarial runtime evaluation ran.
- **Companion:** fallback grounds answers in stored CarePath context; no live Gemini/graph/database call ran.
