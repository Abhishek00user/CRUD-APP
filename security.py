# We'll put password hashing and JWT-related functionality here. The purpose of this file is to return a JWT token when the user logs in with correct credentials.
from datetime import datetime, timedelta, timezone

import dotenv
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from pwdlib import PasswordHash
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import User
from pwdlib import PasswordHash

# ---------------------------------------------------------
# JWT CONFIGURATION
# ---------------------------------------------------------

load_dotenv() # Load env var from .env file
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ---------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------

# Recommended password hashing configuration .This uses the Argon2id algorithm
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # Convert plaintext password into a secure hash
    return password_hash.hash(password)

def verify_password(plain_password: str,hashed_password: str) -> bool:  # the parameters are the password entered by the user and the hashed password stored in the db
    # Check whether the supplied password matches
    # the hash stored in the database
    return password_hash.verify(
        plain_password,
        hashed_password
    )

# ---------------------------------------------------------
# OAUTH2 SCHEME
# ---------------------------------------------------------

# FastAPI will look for:
# Authorization: Bearer <token>
# tokenUrl tells Swagger where users can obtain a token.
# oauth2_scheme's main job here is to extract the bearer token from the request.
oauth2_scheme = OAuth2PasswordBearer(  # this is a dependency that will be used in the endpoints that require authentication. It will extract the token from the authorization header and validate it. if the token is valid , it will return username else error. tokenUrl is the endpoint where users can obtain the token
    tokenUrl="/auth/login"
)

# ---------------------------------------------------------
# JWT CREATION
# ---------------------------------------------------------

def create_access_token(
    username: str,
    expires_delta: timedelta | None = None  # this parameter is used to specify how long the token will be valid for. default value is None, which means 15 minutes if not specified
    ) -> str:

    # Data that will be stored inside the JWT
    data = {
        "sub": username # subject is username
    }

    # Calculate token expiration time
    if expires_delta:
        expire = (
            datetime.now(timezone.utc)
            + expires_delta             # if expires_delta(time) is provided, we use that to calc the expiration time by adding it to current time
        )
    else:
        expire = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        )

    # Add expiration to the JWT payload
    data.update({
        "exp": expire
    })

    # Create and sign the JWT by encoding the data with secret key and algorithm
    encoded_jwt = jwt.encode(
        data,           # data contains the payload of JWT, which includes the username and expiration time
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

# ---------------------------------------------------------
# GET CURRENT USER
# ---------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme), # fastAPI automatically extract the token and pass to function
    db: Session = Depends(get_db)
):
    # Error returned when the token is invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )
    # now we will decode the token using the same algo which was used when hashing for the first time and try to match it from db
    try:
        payload = jwt.decode( 
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]
        )

         # Extract username from "sub"
        username = payload.get("sub")

        # Token must contain a subject
        if username is None:
            raise credentials_exception

    except InvalidTokenError:           # here InvalidTokenError is a built-in exception that is raised when token is invalid

        # Token is invalid, expired, malformed, etc.
        raise credentials_exception

    # Find user in database
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    # User must exist
    if user is None:
        raise credentials_exception

    return user

# defining a function for verifying role
def require_roles(allowed_roles : list[str]):   # multiple roles for one person as admins and teachers both should be able to delete

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        # if role of the user in database does not match with the role that cliend is specifying then error
        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker

# Request
#    ↓
# require_role("admin")
#    ↓
# get_current_user()
#    ↓
# Decode JWT
#    ↓
# Find user
#    ↓
# Check role
#    ↓
# role == "admin" ?