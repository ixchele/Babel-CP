from typing import Optional
from pydantic import BaseModel

class Problem(BaseModel):
    id: int
    title: str
    preview: str
    difficulty: str
    status: str
    content: str

class SubmissionRequest(BaseModel):
    problem_id: int
    language: str
    code: str

class SubmissionResponse(BaseModel):
    submission_id: str
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str
