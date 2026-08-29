# End-to-End Test Plan

1. Create isolated PostgreSQL test database and real secrets.
2. Start `uvicorn backend.app.main:app`; confirm `/health` and route registration.
3. Register User A and User B, login each, retain separate JWTs.
4. Confirm every protected resource rejects User B access to User A data.
5. For User A: submit an initial symptom, call medical analysis, confirm persisted `PatientUpdate` and `AIAnalysis`.
6. Submit a worsening update through Companion; confirm it persists, invokes the clinical graph, creates a second analysis linked by `previous_analysis_id`, and records changed factors.
7. Confirm timeline includes prior and current updates, and Companion explains the new result in English and Hindi.
8. Test configured emergency messages and verify Safety escalation without reassurance.
9. Upload valid/invalid/empty/oversized files, then test OCR/Vision/RAG failures independently.
10. Run browser tests for login, dashboard, upload, analysis, timeline, settings, Companion, and voice-supported browser behavior.
