# CarePath AI — Final Engineering Validation Report

## 1. Environment — YELLOW / PARTIAL

- Node `v24.18.0`, npm `11.16.0`; frontend TypeScript validation is available.
- Python `3.13.13` is present. Both the user-level installation and a workspace-targeted installation were attempted, but the project interpreter still cannot import FastAPI or pytest (the workspace `fastapi` directory is incomplete and has no importable module). Backend runtime and pytest validation are therefore **BLOCKED**. This is an environment/package-installation issue, not a passing backend validation.
- PostgreSQL connectivity, ChromaDB availability, and Gemini configuration were not verifiable without a working backend runtime and non-secret deployment configuration.
- `JWT_SECRET_KEY` and `PASSWORD_SALT` must be non-placeholder environment values before startup.

## 2. Changes validated

### PASS — controlled clinical-workflow failure

The medical analysis route now awaits the asynchronous LangGraph workflow with `ainvoke`. A graph failure rolls back and returns HTTP 503 with a patient-safe unavailable message; it no longer persists a fabricated fallback analysis.

### PASS — Companion to clinical workflow handoff

The Companion now classifies conversational messages as existing-result explanation, new symptom, symptom change/treatment failure, or urgent safety concern. For new clinical needs it persists the patient's message as a `PatientUpdate`, invokes the existing authenticated `/medical/analyze` handler and therefore the existing clinical LangGraph workflow, then returns a bounded explanation. It does not create a second clinical system. Urgent terms are explicitly routed through the same clinical workflow, whose Safety Agent remains authoritative.

### PASS — frontend static validation

`npm run lint` completes successfully in `frontend`.

### BLOCKED — frontend production bundle

`npm --prefix frontend run build` reaches Vite but fails before bundling because esbuild is denied access while resolving `frontend/vite.config.ts` (`Cannot read directory "../../../..": Access is denied`). This sandbox filesystem failure is recorded separately from TypeScript validation.

### PASS — security wiring retained

Ownership-scoped Companion conversations and the Phase 3B JWT/resource controls remain in place. New handoff uses `current_user.user_id`; it does not trust a frontend patient ID.

## 3. Tests

| Area | Status | Evidence |
| --- | --- | --- |
| Frontend TypeScript | PASS | `cd frontend; npm run lint` |
| Frontend production build | BLOCKED | esbuild sandbox access denied while resolving Vite configuration |
| Python syntax | PASS | `python -m py_compile …` on changed modules |
| Final hardening regression tests | BLOCKED | `pytest` cannot be imported by the project interpreter |
| FastAPI startup / HTTP E2E | BLOCKED | `fastapi` cannot be imported by the project interpreter |
| Database / PostgreSQL | BLOCKED | requires reachable configured database |
| Gemini, RAG, ChromaDB | BLOCKED | requires working backend configuration; ChromaDB is not installed/verified |
| Browser E2E / voice | NOT IMPLEMENTED | no browser automation suite configured |

## 4. Performance — BLOCKED

No P50/P95/P99 values are reported because backend requests could not be executed honestly. The Companion context performs eight bounded patient-scoped queries per request; this is a candidate for measurement and consolidation after the backend environment is working. LLM, document/OCR, RAG, and per-agent timing instrumentation are not yet implemented.

## 5. AI subsystem validation — YELLOW / PARTIAL

- **Clinical reasoning and longitudinal state:** context is injected and consumed by Timeline and Clinical Reasoning; real execution is blocked by the environment.
- **Safety:** deterministic red-flag logic exists and Companion urgent handoffs reach the clinical workflow; runtime validation is blocked.
- **Vision/OCR:** interfaces and heuristic/fallback behavior exist, but real clinical-image/OCR accuracy has not been validated. They must not be represented as validated medical intelligence.
- **RAG:** not validated; ChromaDB availability is unverified. An evidence-unavailable response path should be added before production.
- **Hallucination tests:** NOT IMPLEMENTED as runtime tests. Companion prompt and deterministic fallback prohibit diagnosis/fabrication, but this is not a substitute for adversarial evaluation.

## 6. Failure handling — YELLOW / PARTIAL

LLM failure in Companion falls back only to stored CarePath data. Clinical graph failure is now a safe 503 rather than a fabricated analysis. Agent-level partial-failure recovery, database outage integration tests, upload corruption/size/type validation tests, and frontend unavailable-state coverage remain incomplete.

## 7. Production readiness

| Area | Assessment |
| --- | --- |
| Core product | YELLOW — code is present; backend cannot be started in this interpreter |
| Security | YELLOW — controls are implemented; HTTP regression suite is blocked |
| Reliability | YELLOW — graph failure now safe; partial-agent recovery incomplete |
| Performance | RED — no honest runtime measurements |
| AI validation | RED — no clinical-quality validation completed |
| Companion | YELLOW — patient-scoped routing/handoff implemented; E2E blocked |
| Deployment | RED — validate the Python environment and production services first |

## 8. Reproduction commands

```powershell
# Ensure this interpreter can import its installed site-packages, then:
python -m pip install -r backend/requirements.txt
python -m pip install langgraph pytest PyJWT sqlalchemy python-dotenv
$env:JWT_SECRET_KEY = '<random-32+-character-secret>'
$env:PASSWORD_SALT = '<random-16+-character-salt>'
python -m uvicorn backend.app.main:app --reload

cd frontend
npm ci
npm run lint
```

Then run `python -m pytest tests/test_final_hardening.py tests/test_companion.py -q` and the authenticated API/E2E suites against an isolated test database.
