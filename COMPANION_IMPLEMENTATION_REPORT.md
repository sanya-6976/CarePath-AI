# CarePath Companion — Phase 3A Implementation Report

## Status

**PARTIAL, functional implementation.** The companion UI, protected API, patient-scoped context retrieval, persisted conversation memory, preferences, Hindi/English request behavior, browser voice input/output, LangGraph companion workflow, and fallback grounding are implemented. A configured `GEMINI_API_KEY` enables real server-side LLM answers. An end-to-end run against a production-authenticated patient and configured LLM was not possible in this workspace.

## Files created

- `backend/app/api/v1/endpoints/companion.py`
- `backend/app/agents/companion_graph.py`
- `frontend/src/components/CarePathCompanion.tsx`
- `frontend/src/services/companionService.ts`
- `frontend/src/i18n.ts`
- `tests/test_companion.py`

## Files modified

- `backend/app/main.py` — companion router registration.
- `database/models.py` — `CompanionConversation`, `CompanionMessage`, and `UserPreference` models.
- `frontend/src/layouts/DashboardLayout.tsx` — one global authenticated mount.
- `frontend/src/context/PreferencesContext.tsx` and `frontend/src/pages/SettingsPage.tsx` — persistent language and companion preferences.

## Backend and data flow

`POST /api/v1/companion/chat` authenticates with the existing JWT dependency, derives the owner from `current_user.user_id`, gathers bounded records from the existing tables, saves the user and assistant messages, and responds in `en` or `hi`. `GET /api/v1/companion/conversations/{id}` also scopes reads to the authenticated owner. `PUT /api/v1/companion/preferences` persists settings.

**REAL:** ownership check, context retrieval, conversation persistence, existing server-side Gemini client use when configured, deterministic record-grounded fallback.

**REAL:** `backend/app/agents/companion_graph.py` is a dedicated LangGraph workflow for the ownership-scoped context and generated companion response. It deliberately does not invoke or modify the 11-agent clinical workflow because it only explains persisted results.

**PARTIAL:** questions requiring a new clinical assessment are constrained by the prompt but are not yet automatically handed off to the existing clinical workflow.

**NOT IMPLEMENTED:** server-side browser-independent transcription/TTS, migration tooling for existing deployed databases, automated browser E2E voice tests, and an authenticated production LLM integration test.

## Safety and security

The frontend never sends a patient id. The backend obtains the user from the bearer token and filters every query by that identity; conversation IDs are also owner-scoped. Documents are only used as filenames, not untrusted raw text. The prompt forbids diagnosis, fabrication, and safety override; the fallback is sourced only from stored fields and says when data is unavailable.

## Tests performed

- Static companion router and ownership tests in `tests/test_companion.py`.
- `npm run lint` completed successfully in `frontend`.
- Python syntax compilation completed successfully for the changed backend modules; full FastAPI and pytest runtime tests were blocked because the current Python environment lacks the declared dependencies (`fastapi`, `pytest`, and LangGraph).
- Existing clinical workflow was not modified.
