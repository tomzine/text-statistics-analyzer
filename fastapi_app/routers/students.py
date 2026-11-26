from fastapi import (
    APIRouter,
    Depends, 
    HTTPException,
    Query
)
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload

from typing import Literal

from .courses import Course, CourseResponse

from ..database import get_db
from ..models import (
    StudentDB,
    SchoolClass,
    Course,
    UserDB
)
from ..schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentWithDetailsResponse,
    StudentPageResponse,
    MessageResponse
)
from ..security import get_current_user, require_admin


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
    "/",
    response_model=list[StudentResponse],
    dependencies=[Depends(get_current_user)]
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


# ADVANCED SEARCH ENDPOINT
@router.get(
    "/search",
    response_model=StudentPageResponse
)
def search_students(

    # Search by name
    search: str | None = None,

    # Age filters
    min_age: int | None = Query(default=None, ge=0),
    max_age: int | None = Query(default=None, ge=0),

    # Relatiohnship filters
    school_class_id: int | None= Query(default=None, ge=1),
    course_id : int | None = Query(default=None, ge =1),

    # Sorting
    sort_by: Literal["id", "name", "age", "grade"] = "id",
    descending: bool = False,

    #Pagination
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),

    db: Session = Depends(get_db)
):

    # 1. Validate age range
    if (
        min_age is not None
        and max_age is not None
        and min_age>max_age
    ):
        raise HTTPException(
            status_code=422,
            detail="min_age cannot be greater than max_age"
        )
    
    # 2. Build filters
    conditions = []

    if search and search.strip():
        conditions.append(
            StudentDB.name.ilike(f"%{search.strip()}%")
        )   

    if min_age is not None:
        conditions.append(
            StudentDB.age >= min_age
        )    

    if max_age is not None:
        conditions.append(
            StudentDB.age <= max_age
        ) 

    if school_class_id is not None:
        conditions.append(
            StudentDB.school_class_id == school_class_id
        )

    if course_id is not None:
        conditions.append(
            StudentDB.courses.any(Course.id == course_id)
        )

    # 3. Count matching students
    count_statement = (
        select(func.count(StudentDB.id))
        .where(*conditions)
    )

    total = db.scalar(count_statement) or 0

    # 4. Build SELECT query
    statement = (
        select(StudentDB)
        .where(*conditions)
    )

    # 5. select sorting column safely
    sort_columns = {
        "id": StudentDB.id,
        "name": StudentDB.name,
        "age": StudentDB.age,
        "grade": StudentDB.grade
    }

    sort_column = sort_columns[sort_by]

    if descending:
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    # 6. Calcuate pagination offset
    offset_value = (page - 1) * page_size

    # 7. Apply pagination
    statement = statement.offset(
        offset_value
    ).limit(page_size)

    # 8. Execute query
    students = db.scalars(statement).all()

    # 9. Calculate total pages
    total_pages = (total + page_size -1) // page_size

    # 10. Return structured response
    return {
        "items": students,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
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
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)]
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
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

