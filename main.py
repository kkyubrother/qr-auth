import os
import string
import random
import datetime
from typing import Annotated, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel import Field, SQLModel, create_engine, Relationship
from sqlmodel import Session

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


from telegram import Bot


# TELEGRAM_BOT_TOKEN = "6072782752:AAHYSDVBBYmS76yql6xU9FpI-18KZH0-Bfw"
TELEGRAM_BOT_TOKEN = "7696420364:AAG6tQ05lY3dCS0C1XJqHUJ9T-TThX88R4w"

# Telegram Bot Token
bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def generate_user_image_korean_to_bytes(name, meal, is_target):
    # 이미지 크기 및 배경 설정
    img_width, img_height = 500, 300
    background_color = "#f0f8ff"  # 밝은 파란색
    text_color = "#000000"  # 검정색
    highlight_color = "#008000" if is_target else "#ff0000"  # 초록색(대상자) 또는 빨간색(비대상자)

    # 인증 시간
    timestamp = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")

    # 이미지 생성
    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # 폰트 설정 (업로드된 한글 폰트 경로 사용)
    try:
        font_path = os.path.join(os.getcwd(), 'static', 'fonts', 'NanumGothic.ttf')  # 업로드된 폰트 파일 경로
        font = ImageFont.truetype(font_path, size=24)
        title_font = ImageFont.truetype(font_path, size=28)
        highlight_font = ImageFont.truetype(font_path, size=30)
    except IOError:
        return None, "업로드된 폰트를 불러오지 못했습니다. 경로를 확인하세요."

    # 제목 텍스트
    title = "큐알 인증"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width, title_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((img_width - title_width) / 2, 20), title, fill="#4682b4", font=title_font)

    # 본문 텍스트
    text = (
        f"이름: {name}\n"
        f"식사: {'점심' if meal == 'lunch' else '저녁'}\n"
        f"인증 시간: {timestamp}"
    )
    text_x, text_y = 50, 80
    draw.multiline_text((text_x, text_y), text, fill=text_color, font=font, spacing=10)

    # 대상자 여부 강조 텍스트
    target_text = "식사 대상자입니다" if is_target else "식사 대상자가 아닙니다"
    draw.text((text_x, text_y + 120), target_text, fill=highlight_color, font=highlight_font)

    # 이미지를 BytesIO에 저장
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes, None


async def generate_user_image_korean_to_bytes2(name, department, duty, meal, is_target):
    # 이미지 크기 및 배경 설정
    img_width, img_height = 500, 400
    background_color = "#f0f8ff"  # 밝은 파란색
    text_color = "#000000"  # 검정색
    highlight_color = "#008000" if is_target else "#ff0000"  # 초록색(대상자) 또는 빨간색(비대상자)

    # 이모지 추가
    # emoji = "✔️" if is_target else "❌"
    # emoji = "\u2714" if is_target else "\u274C"
    emoji = ""

    # 인증 시간
    timestamp = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")

    # 이미지 생성
    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    # 폰트 설정 (업로드된 한글 폰트 경로 사용)
    try:
        # font_path = "/mnt/data/NanumGothic.ttf"  # 업로드된 폰트 파일 경로
        font_path = os.path.join(os.getcwd(), 'static', 'fonts', 'NanumGothic.ttf')  # 업로드된 폰트 파일 경로
        font = ImageFont.truetype(font_path, size=24)
        title_font = ImageFont.truetype(font_path, size=28)
        highlight_font = ImageFont.truetype(font_path, size=30)
    except IOError:
        return None, "업로드된 폰트를 불러오지 못했습니다. 경로를 확인하세요."

    # 제목 텍스트
    title = "큐알 인증"
    # title_width, title_height = draw.textsize(title, font=title_font)

    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width, title_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((img_width - title_width) / 2, 20), title, fill="#4682b4", font=title_font)

    # 본문 텍스트
    text = (
        f"이름: {name}\n"
        f"부서: {department}\n"
        f"직책: {duty}\n"
        f"식사: {'점심' if meal == 'lunch' else '저녁'}\n"
        f"인증 시간: {timestamp}"
    )
    text_x, text_y = 50, 80
    draw.multiline_text((text_x, text_y), text, fill=text_color, font=font, spacing=10)

    # 대상자 여부 강조 텍스트
    target_text = f"대상자 여부: {emoji} {'예' if is_target else '아니오'}"
    draw.text((text_x, text_y + 200), target_text, fill=highlight_color, font=highlight_font)

    # 이미지를 BytesIO에 저장
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes, None

async def send_qr_to_user(chat_id, name, meal, is_target):
    # QR 이미지 생성
    img_bytes, error = await generate_user_image_korean_to_bytes(
        name=name,
        # department=department,
        # duty=duty,
        meal=meal,
        is_target=is_target
    )

    if error:
        print(f"Error generating image: {error}")
        return

    await bot.send_message(chat_id=chat_id, text=f"안녕하세요 {name}님! 아래는 인증 QR 정보입니다.")

    # Telegram을 통해 이미지 전송
    try:
        await bot.send_photo(chat_id=chat_id, photo=img_bytes, caption=f"안녕하세요 {name}님! 아래는 인증 QR 정보입니다.")
        print("Image sent successfully!")
    except Exception as e:
        print(f"Failed to send image: {e}")


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    tel: str = Field(regex=r'010-\d{4}-\d{4}')
    department: str
    duty: str
    is_lunch: bool
    is_dinner: bool
    bot_id: int | None = Field(default=None)
    updated_at: datetime.datetime | None = Field(default=None)
    qr_list: list["Qr"] = Relationship(back_populates="user")
    deleted_at: datetime.datetime | None = Field(default=None)


class Qr(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str
    created_at: datetime.datetime | None = Field(default=lambda: datetime.datetime.now(datetime.timezone.utc))
    authed_at: datetime.datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="qr_list")


class UserUpdateDto(SQLModel):
    name: str
    tel: str


class UserCreateDto(SQLModel):
    name: str
    tel: str = Field(regex=r'010-\d{4}-\d{4}')
    department: str
    duty: str
    meal: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:5173",
    "https://qr.scjandrew.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import jwt  # Using PyJWT instead of jose

SECRET_KEY = "R&)$a_u6Q3mJ_gM78MABCGUV$9iEF1Vk"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6 * 60

# Load environment variables
LOGIN_ID = os.getenv("LOGIN_ID", "andrew_qr")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "qr144000!!")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, detail="Could not validate credentials"
        )


@app.post("/api/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != LOGIN_ID or form_data.password != LOGIN_PASSWORD:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/protected")
async def protected_api(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return {"message": f"Hello, {username}! You have access to the protected API."}

# React 정적 파일 디렉토리를 "/assets" 경로로 매핑
app.mount("/web/assets", StaticFiles(directory="qr-auth-frontend/dist"), name="assets")

@app.get("/web")
async def serve_root():
    # React 앱의 index.html을 반환
    return FileResponse("qr-auth-frontend/dist/index.html")


@app.get("/api/bot/{bot_id}")
async def get_bot_user(bot_id: int, session: Session = Depends(get_session)):
    try:
        user = session.get(User, int(bot_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="User not found")


@app.put("/api/bot/{bot_id}")
async def put_bot_user(bot_id: int, user_dto: UserUpdateDto, session: Session = Depends(get_session)):
    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel).where(User.deleted_at == None)
    results = session.exec(statement)
    user = results.one()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        user.bot_id = bot_id
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@app.get("/api/user", response_model=list[User])
async def get_user(session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    statement = select(User).where(User.deleted_at == None)
    return session.exec(statement).all()


@app.post("/api/user")
async def post_user(user_dto: User, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel).where(User.deleted_at == None)
    results = session.exec(statement)
    user = results.one_or_none()

    if user:
        raise HTTPException(status_code=403, detail="Already exists")

    if not user:
        session.add(user_dto)
        session.commit()

    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel).where(User.deleted_at == None)
    results = session.exec(statement)
    return results.one()


@app.put("/api/user/{user_id}")
async def put_user(user_id: str, user_dto: User, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    user_id = int(user_id)
    statement = select(User).where(User.id == user_id).where(User.deleted_at == None)
    results = session.exec(statement)
    user = results.one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Not Found")

    user.name = user_dto.name
    user.tel = user_dto.tel
    user.department = user_dto.department
    user.duty = user_dto.duty
    user.is_lunch = user_dto.is_lunch
    user.is_dinner = user_dto.is_dinner
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)

    session.add(user)
    session.commit()

    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel).where(User.deleted_at == None)
    results = session.exec(statement)
    return results.one()


@app.delete("/api/user/{user_id}")
async def put_user(user_id: str, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    user_id = int(user_id)
    statement = select(User).where(User.id == user_id)
    results = session.exec(statement)
    user = results.one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Not Found")

    user.name = f"DEL_{user.name}_{datetime.datetime.now(datetime.timezone.utc)}"
    user.is_lunch = False
    user.is_dinner = False
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    user.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(user)
    session.commit()


@app.get("/api/bot/{bot_id}/qr")
async def get_user_qr(bot_id: str, session: Session = Depends(get_session)):
    bot_id = int(bot_id)
    statement = select(User).where(User.bot_id == bot_id).where(User.deleted_at == None)
    user = session.exec(statement).one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now_time = datetime.datetime.now(datetime.timezone.utc)
    # is_lunch_time = 11 <= (now_time + datetime.timedelta(hours=9)).hour < 13
    # is_dinner_time = 17 <= (now_time + datetime.timedelta(hours=9)).hour < 19

    # if is_lunch_time and not user.is_lunch:
    #     raise HTTPException(status_code=403, detail="Not lunch target")
    #
    # if is_dinner_time and not user.is_dinner:
    #     raise HTTPException(status_code=403, detail="Not dinner target")

    if len(user.qr_list) > 0:
        latest_qr = user.qr_list[-1]

        # created_at 필드가 offset-naive인 경우 UTC-aware로 변환
        if latest_qr.authed_at and latest_qr.authed_at.tzinfo is None:
            latest_qr.authed_at = latest_qr.authed_at.replace(tzinfo=datetime.timezone.utc)

        if latest_qr.authed_at is not None and latest_qr.authed_at > (now_time + datetime.timedelta(hours=2)):
            raise HTTPException(status_code=403, detail="Already Authed")

    code = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(10)])
    qr = Qr(code=code, user_id=user.id, created_at=datetime.datetime.now(datetime.timezone.utc))
    session.add(qr)
    user.qr_list.append(qr)
    session.commit()
    session.refresh(qr)

    return qr


@app.post("/api/qr/{code}")
async def get_qr(code: str, session: Session = Depends(get_session)):
    qr = session.exec(
        select(Qr)
        .where(Qr.code == code)
        .where(Qr.authed_at == None)
        .where(Qr.created_at >= (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)))
    ).one_or_none()

    if not qr:
        raise HTTPException(status_code=404, detail="Qr not found")

    qr.authed_at = datetime.datetime.now(datetime.timezone.utc)
    session.add(qr)
    session.commit()
    session.refresh(qr)


    user = qr.user
    if user and user.bot_id:
        now_time = datetime.datetime.now(datetime.timezone.utc)
        is_lunch_time = 11 <= (now_time + datetime.timedelta(hours=9)).hour < 13
        is_dinner_time = 17 <= (now_time + datetime.timedelta(hours=9)).hour < 19

        await send_qr_to_user(
            user.bot_id,
            user.name,
            'lunch' if is_lunch_time else 'dinner',
            user.is_lunch if is_lunch_time else user.is_dinner
        )

    return {"status": "success", "message": f"{user.name}님 인증되었습니다!"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
