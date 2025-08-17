# backend/auth.py
from fastapi import HTTPException, Header, Depends

# Hardcoded credentials for assignment/testing
USERNAME = "akshanshtyagi"
PASSWORD = "password123"

def verify_auth(x_username: str = Header(...), x_password: str = Header(...)):
    """
    Simple authentication dependency.
    - Expects headers:
        x-username: <USERNAME>
        x-password: <PASSWORD>
    """
    if x_username != USERNAME or x_password != PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
