import os
import jwt

from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer


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
    extracted_jwt : str = Depends(oauth2_scheme)
) :
    """
    extracted_jwt: is the token extaracted from request header
    str: Python type annonation
    Depends(oauth2_scheme) : excute the dependency oauth2_scheme and 
                             injected to extracted_jwt
    """

    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY enviroment variable is missing"
        )


    try:

        payload = jwt.decode(
            extracted_jwt,
            secret_key,
            algorithms=[ALGORITHM]
        )
    
    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    pass