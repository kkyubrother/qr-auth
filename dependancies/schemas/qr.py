import datetime

from pydantic import BaseModel, Field

from dependancies.schemas.users import User


class Qr(BaseModel):
    code: str
    created_at: datetime.datetime | str
    expires_at: datetime.datetime | str


class QrAuth(BaseModel):
    qr: Qr
    user: User
