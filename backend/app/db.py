from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    from app import models, crud
    from app import models_modules  # Import module models
    Base.metadata.create_all(bind=engine)
    
    # Initialize default permissions and roles
    db = SessionLocal()
    try:
        crud.init_default_permissions_and_roles(db)
    finally:
        db.close()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



