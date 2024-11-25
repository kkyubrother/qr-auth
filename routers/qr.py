from fastapi import APIRouter

router = APIRouter()


@router.get("/api/qr")
async def say_hello():
    """

    :return:
    """
    return {"message": f"Hello"}
