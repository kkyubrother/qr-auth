from fastapi import APIRouter

router = APIRouter()


@router.get("/api/bot")
async def post_message():
    """봇 서버에서 전송되는 메세지 webhook

    :return:
    """
    return {"message": f"Hello"}
