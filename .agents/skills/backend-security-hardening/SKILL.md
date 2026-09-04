---
name: Backend Security Hardening
description: Security patterns and hardening practices for the FastAPI backend, including authentication, secrets management, and sanitization.
---

# Backend Security Hardening

This skill defines the standard security patterns for the Airport Digital Helpdesk FastAPI backend. Adhere to these guidelines to ensure the system is secure by design.

## 1. Authentication & Authorization Patterns

Currently, admin endpoints lack authentication. Use FastAPI's dependency injection (`Depends`) to enforce authentication and Role-Based Access Control (RBAC).

**Standard Dependency Chain:**
Define dependencies in `app/core/security.py` or a dedicated `app/modules/auth/dependencies.py`.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token and retrieve user
    user = decode_token_and_get_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user
```

**Protecting Admin Routes:**
```python
from fastapi import APIRouter, Depends
from app.modules.auth.dependencies import require_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/dashboard", dependencies=[Depends(require_admin)])
async def admin_dashboard():
    return {"message": "Welcome to the admin dashboard"}
```

## 2. Password Hashing

Never store operator passwords in plaintext. Use `passlib` with `bcrypt`.

**Implementation in `app/core/security.py`:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

*Migration Note:* When introducing this to existing plaintext databases, implement a migration script or auto-upgrade passwords upon the next successful login.

## 3. Secrets Management

Do not expose secrets like `GROQ_API_KEY` in logs or stack traces. Use `pydantic.SecretStr` in `app/core/config.py`.

```python
from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    GROQ_API_KEY: SecretStr
    # other settings...

    class Config:
        env_file = ".env"
```

* Ensure `.env.example` is always provided with placeholder values (e.g., `GROQ_API_KEY=your_groq_api_key_here`).
* Using `SecretStr` ensures that `print(settings.GROQ_API_KEY)` outputs `**********`, preventing accidental exposure. Use `settings.GROQ_API_KEY.get_secret_value()` when the actual value is needed.

## 4. Input Sanitization & Path Traversal Prevention

Always validate path parameters and file uploads to prevent path traversal and arbitrary file execution.

**Regex-Constrained Path Parameters:**
```python
from fastapi import APIRouter, Path
import re

router = APIRouter()

@router.get("/recordings/{call_id}")
async def get_recording(call_id: str = Path(..., regex="^[a-zA-Z0-9_-]+$")):
    # Validates that call_id contains only safe characters
    pass
```

**File Upload Validation:**
Validate MIME types, limit sizes, and sanitize filenames before saving.
```python
import os
import shutil
from fastapi import UploadFile, HTTPException, status
from werkzeug.utils import secure_filename

async def handle_upload(file: UploadFile):
    if file.content_type not in ["audio/wav", "audio/mpeg"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
    
    filename = secure_filename(file.filename)
    safe_path = os.path.join("/safe/upload/directory", filename)
    
    with open(safe_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
```

## 5. Cryptographically Secure Random

Do not use the `random` module for security-sensitive operations like generating OTPs or session tokens. Use the `secrets` module instead.

**Anti-Pattern (Vulnerable):**
```python
import random
import string

def generate_otp():
    # INSECURE: predictable PRNG
    return ''.join(random.choices(string.digits, k=6))
```

**Correct Implementation:**
```python
import secrets
import string

def generate_otp() -> str:
    # SECURE: cryptographically strong random
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)
```

## 6. CORS Configuration Notes

The current configuration in `app/main.py` is intentionally permissive for development speed:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Must be False if allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)
```
> [!NOTE]
> This is a known dev-mode setting. It should be tightened for production environments, but it is NOT a blocking requirement during current development phases.

**Production Template:**
For production, explicitly whitelist origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://admin.example.com", "https://kiosk.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
*Note on W3C Spec:* You cannot set `allow_credentials=True` when `allow_origins=["*"]`. The browser will block the request.

## 7. Security Checklist

- [ ] All admin routes are protected by a `require_admin` dependency.
- [ ] Passwords are hashed using `passlib[bcrypt]`.
- [ ] Secrets (API keys, DB credentials) use `pydantic.SecretStr`.
- [ ] `.env.example` is present and up-to-date.
- [ ] Path parameters are constrained via Regex (e.g., `Path(..., regex=...)`).
- [ ] File uploads validate MIME types and use sanitized filenames (`secure_filename`).
- [ ] OTPs and tokens are generated using the `secrets` module.

## 8. Companion Skills Cross-References

| Skill | Path | Relationship |
|-------|------|--------------|
| FastAPI Backend Best Practices | `Backend/.agents/skills/backend-fastapi-best-practices/SKILL.md` | Core FastAPI structure and dependency injection rules. |
| Database Management | `Backend/.agents/skills/backend-database-management/SKILL.md` | Connecting auth flows and hashed passwords with SQLAlchemy. |
