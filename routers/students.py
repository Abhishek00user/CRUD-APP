# This is where our API endpoints will be defined via router

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import StudentCreate, StudentUpdate,StudentResponse
import crud
from models import User
from security import get_current_user,require_roles

router = APIRouter(
    prefix="/students",  #  now we don't have to repeatedly write /students.
    tags=["Students"]   # tags are used to group the endpoints in the documentation.
)

# CREATE(teachers and admin can create)
@router.post("/", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["teacher","admin"])) # with this, authentication will be handled automatically for this endpoint.
):

    return crud.create_student(db, student)


# READ ALL (anyone can read)
@router.get("/", response_model=list[StudentResponse])  # list used here because we are returning a list of students. response_model is used to tell FastAPI what the response should look like.
def get_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # this will ensure  AUTHENTICATION on every request to this endpoint.
):

    return crud.get_students(db)


# READ ONE
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    student = crud.get_student(
        db,
        student_id
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# UPDATE(only teachers should update)
@router.put("/{student_id}",response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin","teacher"])
    )
):

    student = crud.update_student(
        db,
        student_id,
        student_data
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# DELETE(only admins should delete)
@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))  # require_role will internally call get_current_user (dependency injection). see required_role function in security.py
):

    student = crud.delete_student(
        db,
        student_id
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return {
        "message": "Student deleted successfully"
    }