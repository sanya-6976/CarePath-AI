# Security Test Results

## Status: BLOCKED — no HTTP runtime

### Executed evidence

- `.env` was examined without printing values. `JWT_SECRET_KEY` and `PASSWORD_SALT` are absent; this is a configuration failure for secure startup.
- Source inspection confirms JWT verification, PBKDF2-HMAC-SHA256 password verification, patient ownership checks, resource ownership checks, owner-scoped conversations, and JWT-derived upload ownership are present.

### Not executed

No User A/User B runtime attempts were possible for profiles, records, uploads, timeline, medications, analyses, care plans, follow-ups, analytics, orchestration, or conversations. Missing/invalid/expired JWT handling and no-password/no-hash response checks are likewise not runtime-verified.

### Required next command

After configuring secrets and a test database: `python -m pytest backend/test_longitudinal.py tests/unit/test_security.py -q`.
