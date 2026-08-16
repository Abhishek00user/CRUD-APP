# We'll put password hashing and JWT-related functionality here. The purpose of this file is to return a JWT token when the user logs in with correct credentials.
from datetime import datetime, timedelta, timezone

import dotenv
import jwt
from jwt.exceptions import InvalidTokenError

from pwdlib import PasswordHash
import os
from dotenv import load_dotenv

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