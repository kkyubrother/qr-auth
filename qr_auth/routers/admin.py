from fastapi import APIRouter
from starlette.requests import Request

from dependancies.db import fake_database
from dependancies.schemas.users import UserCreateRequest, UserUpdateRequest, UserDeleteRequest

router = APIRouter(
    prefix="/api/admin",
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


@router.get("/api/admin/user")
async def list_user(include_delete_user: bool = False):
    """사용자 추가

    :return:
    """
    print(f"사용자 조회: {include_delete_user}")
    return {"message": f"Hello World", "data": fake_database.read_all_users(include_delete_user)}


@router.post("/api/admin/user")
async def add_user(create_user: UserCreateRequest):
    """사용자 추가

    :return:
    """
    print(f"사용자 추가: {create_user}")
    fake_database.add_user(create_user)
    print(fake_database.read_all_users())
    return {"message": f"Hello World"}


@router.put("/api/admin/user")
async def update_user(user: UserUpdateRequest):
    """사용자 정보 변경

    :return:
    """
    print(f"사용자 변경: {user}")
    fake_database.update_user(user.user_id, UserCreateRequest(**user.model_dump(
        exclude={'user_id'}
    )))
    print(fake_database.read_all_users())
    return {"message": f"Hello"}


@router.delete("/api/admin/user")
async def delete_user(user: UserDeleteRequest):
    """사용자 삭제

    :return:
    """
    print(f"사용자 삭제: {user}")
    fake_database.delete_user(user.user_id)
    print(fake_database.read_all_users())
    return {"message": f"Hello"}
