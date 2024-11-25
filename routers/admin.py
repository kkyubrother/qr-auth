from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter(
    prefix="/admin",
)


@router.get("/api/admin")
async def say_hello():
    return {"message": f"Hello"}


@router.get("/api/admin/auth")
async def say_hello():
    """관리자 전용 인증 로직

    ID, PW 입력하여 검증

    :return:
    """
    return {"message": f"Hello"}


@router.post("/api/admin/user")
async def add_user(request: Request):
    """사용자 추가

    :param request:
    :return:
    """
    return {"message": f"Hello"}


@router.put("/api/admin/user")
async def add_user(request: Request):
    """사용자 정보 변경

    :param request:
    :return:
    """
    return {"message": f"Hello"}


@router.delete("/api/admin/user")
async def add_user(request: Request):
    """사용자 삭제

    :param request:
    :return:
    """
    return {"message": f"Hello"}
