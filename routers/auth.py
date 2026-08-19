from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, Token,UserRoleUpdate
import crud

from security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    require_roles
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"] # tags are used to group related endpoints . here we are grouping all authentication related endpoints under the "Authentication" tag
)

# REGISTER
@router.post("/register",response_model = UserResponse)
def register_user(user:UserCreate, db: Session = Depends(get_db)):

    # check whether username already exists
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code= 400,
            details = "User already exists"
        )

    # Hash the  password before storing it
    hashed_password = hash_password(user.password)

    # create new User obj
    new_user = User(
        username = user.username,
        hashed_password = hashed_password,
        role = "student"                    # for authorization purpose
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# LOGIN
@router.post("/login",response_model= Token)
def login(
    form_data : OAuth2PasswordRequestForm = Depends(), # this parameter is used to get the username and password from the request body. It is a dependency that automatically parses the form data and provides it to the function
    db: Session = Depends(get_db)
):
    #check whether the user exists or not
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )
    # if either user does not exist or the login credentials are invalid
    if(not user or not verify_password(form_data.password, user.hashed_password)):  # here not verify_password means that the password provided by user does not match with the pass stored in the database

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

# create a jwt token
     # Create JWT token
    access_token = create_access_token(
        username=user.username,
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# when in admin mode , user role can be updated
@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse
)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),

    # Only admins can reach this endpoint
    current_user: User = Depends(
        require_roles(["admin"])
    )
):

    # Update the user's role,only if the Admin has requested
    user = crud.update_user_role(
        db,
        user_id,
        role_data.role.value
    )

    # User doesn't exist
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user