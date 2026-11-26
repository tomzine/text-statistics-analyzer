from .security import (
    get_password_hash,
    verify_password
)

# Original password
password = "Ahmed123"

# Generate hash
hashed_password = get_password_hash(password)

print("Hashed password:", hashed_password)

# Test correct password
print(
    "Correct password:",
    verify_password(password, hashed_password)
)

# Test incorrect password
print(
    "Incorrect password:",
    verify_password("WrongPassword", hashed_password)
)