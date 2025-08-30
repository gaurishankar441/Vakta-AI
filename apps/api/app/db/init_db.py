from sqlalchemy import inspect
from .session import engine
from .base_class import Base
from app import models  # import all models so they register

def init_db():
    inspector = inspect(engine)
    # For now, just create all tables if not present
    Base.metadata.create_all(bind=engine)
