# CarePath AI - Backend Foundation (FastAPI)

Welcome to the backend foundation for **CarePath AI**, an Autonomous Multi-Agent Healthcare Navigation Platform.

---

## 🏗 Sprint 1 Execution Plan

Sprint 1 focuses on building a production-ready, clean, modular FastAPI backend foundation **before** introducing AI Agents in Sprint 2 (LangGraph).

### Phase 1 Modules (Current Status):
1. ✅ **Module 1: Directory Tree & Core Foundation**
   - Project structure initialization under `/backend`
   - `requirements.txt` & `.env.example`
   - `app/core/config.py` (Pydantic v2 `BaseSettings`)
   - `app/core/security.py` (Bcrypt password hashing & JWT tokens)
   - `app/core/logging.py` (`structlog` structured logging setup)

### Upcoming Modules in Sprint 1:
2. **Module 2: Database Layer & Async Engine**
   - `app/db/session.py` (SQLAlchemy 2.0 Async engine & `get_db` dependency)
   - `app/db/base_class.py` & `app/models/` (User, Patient, MedicalRecord, AuditLog models)
3. **Module 3: Pydantic Schemas & Repository Layer**
   - `app/schemas/` (Request/Response validators)
   - `app/repositories/` (Base CRUD & repository patterns)
4. **Module 4: Service Layer & Business Logic**
   - `app/services/` (Auth Service, Patient Service, Medical Record Service)
5. **Module 5: API Endpoints & FastAPI App Entry Point**
   - `app/api/v1/endpoints/` (auth.py, patients.py, records.py, health.py)
   - `app/main.py` (FastAPI app instance, middlewares, global error handlers)
6. **Module 6: Dockerization & Testing Suite**
   - `Dockerfile`, `docker-compose.yml`, `pytest` test suite

---

## 🛠 Local Setup & Running

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Run development server
uvicorn app.main:app --reload --port 8000
```

---

## 🏛 Architecture Reference
Refer to the **Architecture Command Center** UI in the root directory for interactive visual diagrams of the 15 system architectural topics, API contracts, and database schema.
