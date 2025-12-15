from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Configure connection pooling based on database type
if "postgresql" in settings.database_url:
    # PostgreSQL with proper connection pooling
    engine = create_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using them
        echo=settings.debug
    )
else:
    # SQLite fallback
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_sql(query: str, params: dict = None):
    """Execute raw SQL query with parameters"""
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        conn.commit()
        return result

def execute_sql_fetch(query: str, params: dict = None):
    """Execute raw SQL query and fetch results"""
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()

def execute_sql_fetchone(query: str, params: dict = None):
    """Execute raw SQL query and fetch one result"""
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchone()

async def init_database():
    """
    Initialize database schema by executing SQL files
    This is called once on application startup
    Idempotent - safe to run multiple times (checks schema_version table)
    """
    try:
        # Construct path to scripts directory relative to this file
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        )
        scripts_dir = os.path.join(project_root, 'scripts')
        
        # First, check if already initialized
        with engine.connect() as conn:
            try:
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'booking' AND table_name = 'schema_version'"
                ))
                schema_exists = result.scalar() > 0
            except:
                schema_exists = False
        
        # If already initialized, skip
        if schema_exists:
            logger.info("Database schema already initialized")
            return
        
        # Execute SQL files in order
        sql_files = [
            'schemas/core.sql',
            'schemas/users.sql',
            'schemas/bookings.sql',
            'schemas/payments.sql',
            'procedures/user_procedures.sql',
            'procedures/booking_procedures.sql',
            'procedures/payment_procedures.sql',
            'procedures/search_procedures.sql',
            'procedures/logging_procedures.sql',
            'data/defaults.sql'
        ]
        
        with engine.connect() as conn:
            for sql_file in sql_files:
                sql_path = os.path.join(scripts_dir, sql_file)
                
                if not os.path.exists(sql_path):
                    logger.warning(f"SQL file not found: {sql_path}")
                    continue
                
                with open(sql_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                try:
                    conn.execute(text(sql_content))
                    logger.debug(f"Executed: {sql_file}")
                except Exception as e:
                    logger.error(f"Error executing {sql_file}: {str(e)}")
                    raise
            
            # Record version
            conn.execute(text(
                "INSERT INTO booking.schema_version (version, notes) VALUES ('1.0', 'Initial schema setup')"
            ))
            conn.commit()
        
        logger.info("Database schema initialized successfully (v1.0)")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        raise