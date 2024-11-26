import datetime
from uuid import uuid4

from fastapi import APIRouter

from dependancies.db import fake_database
from dependancies.schemas.qr import Qr

router = APIRouter(
    prefix="/api/qr_auth",
)


@router.get("/")
async def say_hello(include_expired_qr: bool = False):
    """

    :return:
    """
    print("QR 조회:")


    return {"message": f"Hello", 'qr': fake_database.list_qr(include_expired_qr)}


@router.get("/generate")
async def generate_qr():
    """

    :return:
    """
    qr_code = str(uuid4())
    created_at = datetime.datetime.now(datetime.UTC)
    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=1)

    new_qr = Qr(
        qr_code=qr_code,
        created_at=created_at,
        expires_at=expires_at
    )

    return {"message": f"Hello", "qr": fake_database.add_qr(new_qr)}
