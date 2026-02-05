from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
import os


SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

app = FastAPI(title="Neuron Auth Service")
USER_DB = os.getenv("USER_DB", "{}")


class LoginRequest(BaseModel):
    email: str
    password: str


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/login", tags=["Auth"])
async def login(req: LoginRequest):
    stored_password = USER_DB.get(req.email)
    if not stored_password or stored_password != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": req.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/verify", tags=["Internal"])
async def verify(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "user": payload.get("sub")}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
