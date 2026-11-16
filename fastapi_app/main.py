from fastapi import FastAPI

from .database import Base, engine
from . import models

from .routers.students import router as students_router
from .routers.classes import router as classes_router
from .routers.courses import router as courses_router


# Create databse tables
Base.metadata.create_all(bind=engine)


#Create FastAPI application
app = FastAPI(
    title="Student Management API",
    description="A learning project using FastAPI and SQLAlchemy",
    version="1.0.0"
)


# Register routers
app.include_router(students_router)
app.include_router(classes_router)
app.include_router(courses_router)