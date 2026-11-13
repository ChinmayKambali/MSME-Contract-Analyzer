import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

def _normalize_db_url(url: str) -> str:
    """Pin the psycopg2 driver: newer SQLAlchemy defaults postgresql:// to psycopg 3,
    which isn't installed. Also accept the postgres:// scheme some hosts hand out."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    return url

engine = create_engine(
    _normalize_db_url(settings.DATABASE_URL),
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Ensure pgvector extension exists and create database tables."""
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            logger.info("pgvector extension initialized.")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
        # Additive column migrations: safe on both fresh and existing DBs.
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE analysis_records "
                "ADD COLUMN IF NOT EXISTS security_report JSON;"
            ))
            conn.execute(text(
                "ALTER TABLE analysis_records "
                "ADD COLUMN IF NOT EXISTS total_exposure JSON;"
            ))
            conn.execute(text(
                "ALTER TABLE analysis_clause_results "
                "ADD COLUMN IF NOT EXISTS exposure JSON;"
            ))
            conn.execute(text(
                "ALTER TABLE analysis_clause_results "
                "ADD COLUMN IF NOT EXISTS verification JSON;"
            ))
        logger.info("Column migration check complete.")
    except Exception as e:
        logger.warning(f"Database initialization notice/warning: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
