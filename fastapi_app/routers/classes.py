from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SchoolClass, StudentDB
from ..schemas import (
    SchoolClassCreate,
    SchoolClassResponse,
    StudentResponse
)

# Create router
router = APIRouter(
    prefix="/classes",
    tags=["Classes"]
)


# 1. CREATE A CLASS
@router.post(
    "",
    response_model=SchoolClassResponse,
    status_code=201
)
def create_class(
    data:SchoolClassCreate,
    db : Session = Depends(get_db)
):

    # Check if class alerady exists
    existing_class = db.scalar(
        select(SchoolClass).where(
            SchoolClass.name == data.name
        )
    )

    if existing_class:
        raise HTTPException(
            status_code=409,
            detail="This class alerady exists"
        )

    # Create new class
    new_class = SchoolClass(
        name=data.name
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)

    return new_class


# 2. GET ALL CLASSES
@router.get(
    "",
    response_model=list[SchoolClassResponse]
)
def get_classes(
    db: Session = Depends(get_db)
):

    statement = select(SchoolClass)

    classes = db.scalars(statement).all()

    return classes

# 3/ GET ONE CLASS
@router.get(
    "/{class_id}",
    response_model=SchoolClassResponse
)
def get_class(
    class_id:int,
    db:Session = Depends(get_db)
):

    school_class = db.get(SchoolClass, class_id)

    if school_classis is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )
    
    return school_class


# 4. GET STUDENT BELONGING TO A CLASS
@router.get(
    "/{class_id}/students",
    response_model=list[StudentResponse]
)
def get_class_students(
    class_id: int,
    db: Session = Depends(get_db)
):

    # check if class exists
    school_class = db.get(SchoolClass, class_id)

    if school_class is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )
    
    # Build Join query
    statement = (
        select(StudentDB)
        .join(StudentDB.school_class)
        .where(SchoolClass.id == class_id)
    )

    #Zxecute query
    students = db.scalars(statement).all()

    return students