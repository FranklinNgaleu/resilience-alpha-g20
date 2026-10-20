
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pwdlib import PasswordHash
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="Resilience Alpha - Auth Service",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

password_hash = PasswordHash.recommended()
security = HTTPBearer()

JWT_SECRET = os.environ["JWT_SECRET"]
DEMO_EMAIL = os.environ["DEMO_EMAIL"]
DEMO_PASSWORD_HASH = os.environ["DEMO_PASSWORD_HASH"]

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "resilience-alpha-auth"
JWT_AUDIENCE = "resilience-alpha-payment"


class LoginRequest(BaseModel):
    email: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}


@app.post("/auth/login")
def login(payload: LoginRequest):
    valid_email = payload.email == DEMO_EMAIL
    valid_password = password_hash.verify(
        payload.password,
        DEMO_PASSWORD_HASH
    )

    if not (valid_email and valid_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": payload.email,
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=30)
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800
    }


@app.get("/auth/me")
def me(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE
        )
        return {"email": payload["sub"]}

    except (InvalidTokenError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
