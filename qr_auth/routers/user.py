from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter(
    prefix='/api/users',
)


@router.get("/api/user")
async def get_user(request: Request):
    return {"message": f"Hello"}


@router.post("/api/user")
async def signin_user(request: Request):
    """사용자 회원 가입

    :param request:
    :return:
    """
    return {"message": f"Hello"}


@router.get("/api/user/qr")
async def say_hello():
    return {"message": f"Hello"}
