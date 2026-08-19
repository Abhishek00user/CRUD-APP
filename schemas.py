from pydantic import BaseModel
from enum import Enum
# -------------------- ROLE --------------------

class Role(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

# Schema used when an admin changes a user's role
class UserRoleUpdate(BaseModel):
    role:Role
    
# -------------------- STUDENT SCHEMAS--------------------
class StudentCreate(BaseModel):
    name:str
    age:int

# For an update request, we don't really want the user to change the id. So let's create another Pydantic model:
class StudentUpdate(BaseModel):
    name: str
    age: int

# Schema used when returning a student through the API
class StudentResponse(BaseModel):
    id: int
    name: str
    age: int

    # Allows Pydantic to read data from SQLAlchemy objects
    class Config:
        from_attributes = True       #from_attributes=True tells Pydantic:You are allowed to construct this response model by reading attributes from an object.


# -------------------- USER SCHEMAS --------------------

# Data received during registration
class UserCreate(BaseModel):
    username: str
    password: str
#Role should not be supplied by the client , new users will autmatically become student

# Data returned to the client 
# Notice that password is NOT included
class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:   # allows pydantic to read data from SQLAlchemy objects
        from_attributes = True


# Response returned after successful login
class Token(BaseModel):
    access_token: str   # this will be the JWT token that the client will use to authenticate future requests
    token_type: str