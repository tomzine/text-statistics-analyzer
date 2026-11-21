from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Schema for creating a student
class StudentCreate(BaseModel):
    name: str
    age: int
    grade: str
    school_class_id: int | None = None
    email: EmailStr | None = None


# Schema for partially updating a student
class StudentUpdate(BaseModel):
    name: str | None = None
    age : int | None = None
    grade:str | None = None
    school_class_id: int | None = None
    email: EmailStr | None = None


# Schema for returning a student
class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    name : str
    age : int
    grade : str
    school_class_id: int | None 
    email: EmailStr | None 


# Schema for returning a student throught pagination
class StudentPageResponse(BaseModel):

    items: list[StudentResponse]
    
    #How many student in total
    total: int

    # Whcih page it is displaying
    page: int

    # How many students are displayed per page
    page_size: int

    # How many page are availabale
    total_pages: int

# Schema for simple messages
class MessageResponse(BaseModel):
    message: str

# Schema for creating school
class SchoolClassCreate(BaseModel):
    name: str

# schema for returning a school
class SchoolClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# schema for creating a course
class CourseCreate(BaseModel):
    name: str


# Schema for returning a course
class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

# Schema for retrieve students with their class and courses
class StudentWithDetailsResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int 
    grade: str

    school_class: SchoolClassResponse | None
    courses: list[CourseResponse]

# Schema for creating users
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128
    )


# Schema for user response
class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    is_active: bool


# Schema for token response
class Token(BaseModel):

    access_token: str
    token_type: str