from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

DATABASE_URL = "sqlite:///./students.db"

# The engine is responsible for managing communication between our application and the database.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()  # this statement creates a base class for our SQLAlchemy models. All of our models will inherit from this base class, which provides the necessary functionality for interacting with the database.

# dependency function to get the database session for each request. This function will be used in our route functions to get a session
def get_db():
    db = SessionLocal()

    try:
        yield db  # it gives the session to the route function and then closes it after request completed
    finally:
        db.close()
