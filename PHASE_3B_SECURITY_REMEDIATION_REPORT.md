# CarePath AI — Phase 3B Security & Longitudinal Context Remediation

## Audit findings before remediation

**Real:** login and registration already used a PBKDF2-HMAC-SHA256 hash and PyJWT signing; the medical router already applied `get_current_user` and patient ownership checks; versioned analyses loaded patient updates into the analysis request state.

**Insecure/missing:** security had committed fallback values for the JWT signing key and password salt. Many adjacent patient endpoints accepted a patient/user ID without an authentication dependency (including profile, uploads, records, timeline, medication, memory, legacy analysis, care plans, follow-ups, doctor bridge, analytics, and orchestration). Profile retrieval supplied mock data when absent. Timeline construction ignored the injected historical updates.

## Remediation implemented

- `core.security` now requires a random environment-supplied `JWT_SECRET_KEY` (with legacy `SECRET_KEY` only as a deployment compatibility alias) and a `PASSWORD_SALT`; placeholders, missing values, and short values are rejected. No signing-secret fallback remains.
- `.env.example` documents `JWT_SECRET_KEY=REPLACE_WITH_STRONG_RANDOM_SECRET`; `.gitignore` already excludes `.env` files.
- Passwords remain hashed before persistence and are verified using constant-time comparison. Neither login nor registration returns a password/hash.
- Added reusable resource ownership and care-team role helpers.
- Protected patient profile, uploads, records, timeline, memory, medications, analysis, follow-up, care-plan, doctor bridge, analytics, and agent orchestration routes. Uploads now derive the stored owner from the authenticated JWT rather than the submitted form `patient_id`.
- Patient profile reads no longer fabricate a fallback patient record.
- The medical router continues to retrieve ordered `PatientUpdate` records and inject them as `historical_context`, and the Timeline Agent now adds those events into its chronology. Clinical reasoning now recognizes prior-history progression as well as the current message.

## Verification

- Python compilation completed for every changed security, endpoint, and longitudinal-node module.
- Static checks verify the required secret policy, the actual `carepath_graph.invoke(initial_state)` call with `historical_context`, and longitudinal timeline consumption.

## Remaining validation

The local Python environment does not have FastAPI, pytest, or LangGraph installed, so authenticated HTTP integration tests and the existing longitudinal test could not be run here. Install the repository requirements and set a non-placeholder `JWT_SECRET_KEY` and `PASSWORD_SALT` before starting the backend. No clinical node or routing behavior was removed or replaced.
