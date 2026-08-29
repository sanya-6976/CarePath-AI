# Performance Report

## Status: BLOCKED

No latency percentile or concurrency figures are reported because the FastAPI runtime could not start honestly.

## Measurement plan

Measure P50/P95 for authenticated API, total LangGraph run, per-agent execution history, database context retrieval, RAG, upload/OCR, Gemini, and Companion responses. Test 1, 5, 10, and 25 concurrent patients against an isolated environment.

## Candidate bottlenecks to measure

- Companion currently performs bounded context queries across profile, analyses, recommendations, updates, symptoms, medications, files, and timeline.
- Clinical agents are mostly ordered sequentially for safety.
- External Gemini, OCR, and ChromaDB calls may dominate latency.

No optimization was applied without measurements.
