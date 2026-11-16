from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .courses import Course, CourseResponse

from ..database import get_db
from ..models import StudentDB, SchoolClass
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentWithDetailsResponse,
    MessageResponse
)


# Create router
router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# 1. CREATE STUDENT
@router.post(
    "",
    response_model=StudentResponse,
    status_code=201
)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db)
):

    if data.school_class_id is not None:
        
        school_class = db.get(
            SchoolClass,
            data.school_class_id
        )

        if school_class is None:
            raise HTTPException(
                status_code=404,
                detail="School class not found"
            )

    new_student = StudentDB(**data.model_dump())

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


#  2. GET ALL STUDENTS
@router.get(
    "",
    response_model=list[StudentResponse]
)
def get_students(
    db: Session = Depends(get_db)
):

    students = db.scalars(
        select(StudentDB)
    ).all()

    return students


# 8. GET ALL INFORMATION ABOUT STUDENT 
@router.get(
    "/with-details",
    response_model=list[StudentWithDetailsResponse]
)
def get_student_with_details(
    db: Session = Depends(get_db)
):

    statement = (
        select(StudentDB)
        .options(
            joinedload(StudentDB.school_class),
            selectinload(StudentDB.courses)
        )
    )

    students = db.scalars(statement).all()

    return students


# 3. GET ONE STUDENT
@router.get(
    "/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id:int,
    db: Session = Depends(get_db)
):

    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    return student


# 4. UPDATE STUDENT (PUT)
@router.put(
    "/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id:int,
    data: StudentCreate,
    db: Session = Depends(get_db)
):

    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    student.name = data.name
    student.age = data.age
    student.grade = data.grade

    db.commit()
    db.refresh(student)

    return student


# 5. DELETE STUDENT
@router.delete(
    "/{student_id}",
    response_model=MessageResponse
)
def delete_student(
    student_id: int,
    db: Session =Depends(get_db)
):

    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully"
    }


# 6. PARTIAL UPDATE STUDENT (PATCH)
@router.patch(
    "/{student_id}",
    response_model=StudentResponse
)
def patch_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db)
):

    # Find student
    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Extract provided fields
    update_data = data.model_dump(exclude_unset=True)

    # Prevent empty updates
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fied provided for update"
        )
    
    # Prevent null values
    for field, valye in update_data.items():

        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )
    
    # Update provided fields
    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student

# 7. GET COURSES FOR A STUDENT
@router.get(
    "/{student_id}/courses",
    response_model=list[CourseResponse]
)
def get_student_courses(
    student_id: int,
    db : Session = Depends(get_db)
):

    # check if student is exist
    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    
    # retrive courses
    statement = (
        select(Course)
        .join(Course.students)
        .where(StudentDB.id == student_id)
    )

    courses = db.scalars(statement).all()

    return courses

