import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
try:
    from supabase import create_client, Client
except ImportError:
    create_client, Client = None, None
from dotenv import load_dotenv, find_dotenv

# Base class for SQLAlchemy models
Base = declarative_base()

# Load environment variables from .env file (auto-searches parent directories)
load_dotenv(find_dotenv(usecwd=True))


# --- PostgreSQL Connection (via SQLAlchemy with automatic SQLite fallback) ---
DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

def _init_db_engine():
    global engine, SessionLocal
    if DATABASE_URL:
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        if "+asyncpg" in db_url:
            db_url = db_url.replace("+asyncpg", "", 1)

        try:
            temp_engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 3}
            )
            # Verify actual database connection
            with temp_engine.connect() as conn:
                pass
            engine = temp_engine
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            print("[INFO] Successfully connected to PostgreSQL database.")
            return
        except Exception as err:
            print(f"[WARNING] Primary PostgreSQL database connection error ({err}). Falling back to local SQLite database.")

    # Fallback SQLite Database
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "carepath_local.db").replace("\\", "/")
        sqlite_url = f"sqlite:///{db_path}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Auto-create tables for fallback SQLite DB
        import database.models  # Register declarative models
        Base.metadata.create_all(bind=engine)
        print(f"[OK] Local fallback database ({db_path}) ready.")
    except Exception as sqlite_err:
        print(f"[ERROR] Failed to initialize fallback database: {sqlite_err}")
        engine = None
        SessionLocal = None

_init_db_engine()


def get_db():
    """Dependency to get a database session (useful for FastAPI etc.)"""
    if SessionLocal is None:
        raise Exception("Database engine is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Supabase Client Connection ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
    supabase = None
