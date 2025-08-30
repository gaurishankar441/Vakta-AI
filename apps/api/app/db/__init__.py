from .session import engine, SessionLocal
from .base_class import Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models  # noqa: F401 (ensures models are registered)
    Base.metadata.create_all(bind=engine)
