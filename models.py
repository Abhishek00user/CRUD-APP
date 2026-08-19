from sqlalchemy import Column, Integer, String
from database import Base


class Student(Base):        # Create a SQLAlchemy model called Student . since it inherits from base , sqlalchemy will know that this represents a table
    __tablename__ = "students"

    # Primary key; SQLite automatically generates the ID
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)

# creating a database model for Users who will login to the system
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # here index is used to create an index on the id column for faster lookups
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # never store the actual password

    # User's role
    role = Column(String, default = "student")