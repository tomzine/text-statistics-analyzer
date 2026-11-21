from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import UserDB
from ..schemas import UserCreate, UserResponse, Token
from ..security import (
    get_password_hash,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):

    # 1. Normalize email
    email = str(data.email).strip().lower()

    # 2. Check wether email alreadu exists
    statement = select(UserDB).where(
        UserDB.email == email
    )

    existing_user = db.scalar(statement)

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    
    # 3. Hash the password
    hashed_password = get_password_hash(
        data.password
    )

    # 4. Create UserDB object
    new_user = UserDB(
        email=email,
        hashed_password=hashed_password
    )

    try:
        # 5. Add user to database session
        db.add(new_user)

        # 6. Save changes
        db.commit()

        # 7. Retrieve generated database values
        db.refresh(new_user)
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    
    # 8. Return user
    return new_user


# THE LOGIN ENDPOINT
@router.post(
    "/login",
    response_model=Token,
    status_code=200
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db : Session = Depends(get_db)
):

    # Find the user
    statement = (
        select(UserDB)
        .where(UserDB.email == form_data.username.strip().lower())
    )

    user = db.scalar(statement)

    # Check if the user exsict
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify if the account is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
            
        )

    # Generate the JWT
    payload = {
        "sub" : str(user.id)
    }

    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

    
