import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int
    username: str
    tel: str
    department: str
    duty: str
    lunch: bool
    dinner: bool
    bot_id: int | None = None


class UserCreateRequest(BaseModel):
    username: str = Field(title="이름", pattern=r'[가-힣]{2,}')
    department: str = Field(title='부서', default='')
    tel: str = Field(title='전화번호', pattern=r'^01[016789]-?\d{3,4}-?\d{4}$', examples=['010-0000-0000'])
    duty: str = Field(title='직책', default='')
    lunch: bool = Field(title='점심', default=False)
    dinner: bool = Field(title='저녁', default=False)


class UserCreateResponse(BaseModel):
    success: bool
    detail: str


class UserUpdateRequest(BaseModel):
    user_id: int
    username: str = Field(title="이름", pattern=r'[가-힣]{2,}')
    department: str = Field(title='부서', default='')
    tel: str = Field(title='전화번호', pattern= r'^01[016789]-?\d{3,4}-?\d{4}$', examples=['010-0000-0000'])
    duty: str = Field(title='직책', default='')
    lunch: bool = Field(title='점심', default=False)
    dinner: bool = Field(title='저녁', default=False)


class UserUpdateResponse(BaseModel):
    success: bool
    detail: str


class UserDeleteRequest(BaseModel):
    user_id: int


class UserDeleteResponse(BaseModel):
    success: bool
    detail: str
