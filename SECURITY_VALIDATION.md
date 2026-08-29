# Security Validation

## Implemented controls — PARTIAL runtime verification

- JWT signing requires `JWT_SECRET_KEY` (legacy `SECRET_KEY` is compatibility-only); placeholder/short values are rejected.
- Password hashes use PBKDF2-HMAC-SHA256 and constant-time verification.
- Patient IDs are checked against the authenticated user; resolved resources are ownership checked.
- Companion conversations are owner-scoped.
- Upload ownership derives from the JWT subject, not a submitted patient ID.
- `.env` and local validation environments are ignored by Git.

## Required runtime regression tests — BLOCKED

Run missing/invalid/expired JWT and User A → User B requests for profile, records, timeline, medication, analysis, care plan, follow-up, analytics, orchestration, uploads, and Companion conversations. Expect 401 when unauthenticated and 403/404 without data disclosure when unauthorized.

No secrets, password values, or hashes are included in these reports.
