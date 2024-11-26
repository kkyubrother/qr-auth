import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int
    username: str
    tel: str
    department: str
    bot_id: int | None = None


class UserCreateRequest(BaseModel):
    username: str
    department: str
    tel: str


class UserCreateResponse(BaseModel):
    success: bool
    detail: str


class UserUpdateRequest(BaseModel):
    user_id: int
    username: str | None = None
    department: str | None = None
    tel: str | None = None


class UserUpdateResponse(BaseModel):
    success: bool
    detail: str


class UserDeleteRequest(BaseModel):
    user_id: int


class UserDeleteResponse(BaseModel):
    success: bool
    detail: str
