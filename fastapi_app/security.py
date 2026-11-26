import os
import jwt

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer

from .database import get_db
from .models import UserDB


# 1. Create password hasher
password_hash = PasswordHash.recommended()

# 2. Hash a password
def get_password_hash(password: str) -> str:

    return password_hash.hash(password)

# 3. Verify a password
def verify_password(
    plain_password: str,
    hasehd_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hasehd_password
    )

#JWT CONFIGURATION

ALGORITHM ="HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# CREATE JWT ACCES TOKEN
def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + (expires_delta if expires_delta is not None 
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ))
    )

    to_encode.update({
        "exp":expire
    })

    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY enviroment variable is missing"
        )
    
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=ALGORITHM
    )

    return encoded_jwt


#  schema for Auth2passwordbearer
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
) 

def get_current_user(
    extracted_jwt : str = Depends(oauth2_scheme),
    db : Session = Depends(get_db)
) -> UserDB:
    """
    extracted_jwt: is the token extaracted from request header
    str: Python type annonation
    Depends(oauth2_scheme) : excute the dependency oauth2_scheme and 
                             injected to extracted_jwt
    """

    credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
    )

    # retrive the secret key from .env
    secret_key = os.getenv("SECRET_KEY")

    # check if there is a secret key
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY enviroment variable is missing"
        )

    # decode the jwt token
    try:
        payload = jwt.decode(
            extracted_jwt,
            secret_key,
            algorithms=[ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    # get the user id from payload
    user_id = payload.get("sub")

    # check for the user id not null
    if not user_id :
        raise credentials_exception

    # check if the user id is string
    if not isinstance(user_id, str):
        raise credentials_exception

    # Check that user_id contains only ASCII digits
    if not user_id.isascii() or not user_id.isdigit():
        raise credentials_exception

    # convert the user id to intger
    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception

    # check the user id is positive
    if user_id <= 0:
        raise credentials_exception

    # retrive the user from database
    user = db.get(UserDB, user_id)

    # check if the user not null
    if not user:
        raise credentials_exception

    # check if the user is active
    if not user.is_active:
        raise credentials_exception

    return user


# ADMIN Authorization dependency
def require_admin(
    current_user: UserDB = Depends(get_current_user)
) -> UserDB:

    role = current_user.role

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator privileges required"
        )

    return current_user