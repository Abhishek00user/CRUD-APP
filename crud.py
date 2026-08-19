# this contains all the crud operations for the student model
# this doesn't contain any fastAPI code or exceptions, just the operation logic
from sqlalchemy.orm import Session

from models import Student,User
from schemas import StudentCreate, StudentUpdate


def create_student(db: Session, student: StudentCreate):

    new_student = Student(
        name=student.name,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


def get_students(db: Session):

    return db.query(Student).all()


def get_student(db: Session, student_id: int):

    return (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )


def update_student(
    db: Session,
    student_id: int,
    student_data: StudentUpdate
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if student is None:
        return None

    student.name = student_data.name
    student.age = student_data.age

    db.commit()
    db.refresh(student)

    return student


def delete_student(db: Session, student_id: int):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if student is None:
        return None

    db.delete(student)
    db.commit()

    return student

def update_user_role(
        db: Session,
        user_id: int,
        role: str
):
     # Find the user
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    # User doesn't exist
    if user is None:
        return None

    # Change the user's role
    user.role = role

    # Save the change
    db.commit()

    # Refresh the object
    db.refresh(user)

    return user