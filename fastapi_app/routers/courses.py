from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Course, StudentDB
from ..schemas import (
    CourseCreate,
    CourseResponse,
    StudentResponse,
    StudentCreate,
    MessageResponse
)


router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


# 1. CREATE COURSE
@router.post(
    "",
    response_model=CourseResponse,
    status_code=201
)
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db)
):

    # Check if course already exists
    existing_course = db.scalar(
        select(Course).where(
            Course.name == data.name
        )
    )

    if existing_course:
        raise HTTPException(
            status_code=409,
            detail="Course already exists"
        )

    # Create course
    new_course = Course(name=data.name)

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.post(
    "/{course_id}/students",
    response_model=StudentResponse,
    status_code=201
)
def create_student_in_course(
    course_id: int,
    data: StudentCreate,
    db: Session = Depends(get_db)
):

    # 1. Find the course
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    
    try:
        #2. Create student
        new_student = StudentDB(
            **data.model_dump()
        )

        # 3.Add student to session
        db.add(new_student)

        # 4. Flush to generate student ID
        db.flush()

        # 5. Enroll student in course
        new_student.courses.append(course)

        # 6. Commit all changes together
        db.commit()

    except Exception:
        #7. Cancel uncommitted changes if something fails
        db.rollback()
        raise

    # 8. Refresh student
    db.refresh(new_student)

    return new_student

# 2. GET ALL COURSES
@router.get(
    "",
    response_model=list[CourseResponse]
)
def get_courses(
    db:Session = Depends(get_db)
):

    statement = select(Course)

    courses = db.scalars(statement).all()

    return courses

# 3. GET ONE COURSE
@router.get(
    "/{course_id}",
    response_model=CourseResponse
)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):

    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course

# 4. ENROLL STUDENT IN COURSE
@router.post(
    "/{course_id}/students/{student_id}",
    response_model=MessageResponse,
    status_code=201
)
def enroll_student(
    course_id : int,
    student_id: int,
    db : Session = Depends(get_db)
):

    # Find course
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )
    # Find student
    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Prevent duplicate enrollment
    if course in student.courses:
        raise HTTPException(
            status_code=409,
            detail="Student already enrolled in this course"
        )

    # Create relationship
    student.courses.append(course)

    # Save changes
    db.commit()

    return {
        "message": "Student enrolled succesfully"
    }

# 5. REMOVE STUDENT FROM COURSE
@router.delete(
    "/{course_id}/students/{student_id}",
    response_model=MessageResponse
)
def remove_student(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db)
):

    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    student = db.get(StudentDB, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
 
    
    if course not in student.courses:
        raise HTTPException(
            status_code="404",
            detail="Enrollement not found"
        )

    student.courses.remove(course)

    db.commit()

    return {
        "message": "Student removed from course succesuflly"
    }


# 6. GET STUDENTS IN A COURSE
@router.get(
    "/{course_id}/students",
    response_model=list[StudentResponse]
)
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db)
):

    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    statement = (
        select(StudentDB)
        .join(StudentDB.courses)
        .where(Course.id == course_id)
    )
    
    students= db.scalars(statement).all()
    
    return students