from sqlalchemy import (
    String,
    ForeignKey,
    Table,
    Column
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column, 
    relationship
)

from .database import Base


# ASSOCIATION TABLE
student_courses = Table(
    "student_courses",
    Base.metadata,

    Column(
        "student_id",
        ForeignKey("students.id"),
        primary_key=True
    ),

    Column(
        "course_id",
        ForeignKey("courses.id"),
        primary_key=True
    )

)


# 1. PARENT MODEL : SCHOOL CLASS
class SchoolClass(Base):
    __tablename__="school_classes"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str]= mapped_column(
        String(50),
        unique=True
    )

    # One class has many students
    students: Mapped[list["StudentDB"]] = relationship(
        back_populates="school_class"
    )


# 2. CHILD MODEL : STUDENT
class StudentDB(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(String(100))

    age : Mapped[int]

    grade: Mapped[str] = mapped_column(String(50))

    # Foreign_key
    school_class_id: Mapped[int | None]= mapped_column(
        ForeignKey("school_classes.id"),
        nullable=True
    )

    school_class: Mapped["SchoolClass | None"] = relationship(
        back_populates="students"
    )

    # Many-to-Many relationship
    courses: Mapped[list["Course"]] = relationship(
        secondary=student_courses,
        back_populates="students"
    )


# COURSE MODEL
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True
    )

    # One course has many students
    students : Mapped[list["StudentDB"]] = relationship(
        secondary=student_courses,
        back_populates="courses"
    )