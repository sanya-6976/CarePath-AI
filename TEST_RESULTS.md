# Test Results

## Executed

| Command | Result |
| --- | --- |
| `python -m py_compile` on changed endpoint, security, and test modules | PASS |
| Static handoff assertion (`await carepath_graph.ainvoke`, Companion await) | PASS |
| `npm --prefix frontend run lint` | PASS |
| `npm --prefix frontend run build` | BLOCKED — esbuild filesystem access denied in sandbox |
| `python -m pytest …` | BLOCKED — `pytest` is not importable by active interpreter |
| FastAPI route/startup import | BLOCKED — `fastapi` is not importable by active interpreter |

## Not executed

Authenticated API E2E, user-isolation regression, database versioning, LangGraph execution, RAG, OCR/Vision, browser/voice, adversarial, and performance tests require a working Python environment plus configured services. They are not claimed as passing.
