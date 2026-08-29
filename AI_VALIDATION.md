# AI Validation

## Implemented but not clinically validated

Clinical reasoning, Safety, Timeline, referral, care planning, and Companion routing are code-integrated. Longitudinal updates are injected into graph state and used by timeline/reasoning nodes. The Companion falls back only to stored CarePath context and routes new clinical needs to the existing workflow.

## Not validated

- Vision: no technical or clinical image dataset evaluation was run.
- OCR: no extraction accuracy test was run.
- RAG: ChromaDB retrieval/source relevance was not run; do not claim guideline grounding until tested.
- Gemini: no live model run, timeout, rate-limit, malformed-response, or adversarial evaluation was run.
- Hallucination suite: not run. Required prompts include demands for certainty, fabricated labs, unsupported dosages, ignored safety, and unsafe reassurance.

CarePath remains healthcare navigation support, not a diagnostic or prescribing system.
