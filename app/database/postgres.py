from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.document import Base
from contextlib import contextmanager

class PostgresDB:
    """PostgreSQL database manager"""
    
    def __init__(self):
        self.engine = create_engine(settings.POSTGRES_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ PostgreSQL tables created")
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# Global instance
postgres_db = PostgresDB()