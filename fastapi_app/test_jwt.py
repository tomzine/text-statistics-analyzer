import os
import jwt

from security import create_access_token

#GENERATING THE TOKEN
# User information
user_data = {
    "sub": "1",
    
}

# Generate token
token = create_access_token(user_data)

# VERIFY TOKEN
secret_key = os.getenv("SECRET_KEY")

decoded_token = jwt.decode(
    token,
    secret_key,
    algorithms=["HS256"]
)

print(decoded_token)