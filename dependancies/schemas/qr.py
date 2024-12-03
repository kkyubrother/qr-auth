import datetime

from pydantic import BaseModel, Field

from dependancies.schemas.users import User


class Qr(BaseModel):
    qr_code: str = Field(title="qr 내부 코드")
    created_at: datetime.datetime | str = Field(title="생성 일시")
    expires_at: datetime.datetime | str = Field(title="생성 일시")


class QrAuth(BaseModel):
    qr: Qr
    user: User


class QrAuthCreateRequest(BaseModel):
    qr_auth_id: int
    qr_code: str
    user_id: int
    created_at: datetime.datetime | str
