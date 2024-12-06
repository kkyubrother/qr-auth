import string
import random
import datetime
from typing import Annotated, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel import Field, SQLModel, create_engine, Relationship
from sqlmodel import Session


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    tel: str
    department: str
    duty: str
    is_lunch: bool
    is_dinner: bool
    bot_id: int | None = Field(default=None)
    updated_at: datetime.datetime | None = Field(default=None)
    qr_list: list["Qr"] = Relationship(back_populates="user")


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
    print("created")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/bot/{bot_id}")
async def get_bot_user(bot_id: int, session: Session = Depends(get_session)):
    user = session.get(User, bot_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/api/bot/{bot_id}")
async def put_bot_user(bot_id: int, user_dto: UserUpdateDto, session: Session = Depends(get_session)):
    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel)
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
async def get_user(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@app.post("/api/user")
async def post_user(user_dto: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel)
    results = session.exec(statement)
    user = results.one_or_none()

    if user:
        raise HTTPException(status_code=403, detail="Already exists")

    if not user:
        session.add(user_dto)
        session.commit()

    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel)
    results = session.exec(statement)
    return results.one()


@app.put("/api/user/{user_id}")
async def put_user(user_id: str, user_dto: User, session: Session = Depends(get_session)):
    user_id = int(user_id)
    statement = select(User).where(User.id == user_id)
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

    statement = select(User).where(User.name == user_dto.name).where(User.tel == user_dto.tel)
    results = session.exec(statement)
    return results.one()


@app.delete("/api/user/{user_id}")
async def put_user(user_id: str, session: Session = Depends(get_session)):
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
    session.add(user)
    session.commit()




@app.get("/api/bot/{bot_id}/qr")
async def get_user_qr(bot_id: str, session: Session = Depends(get_session)):
    bot_id = int(bot_id)
    user = session.exec(select(User).where(User.bot_id == bot_id)).one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now_time = datetime.datetime.now(datetime.timezone.utc)
    print(now_time)
    is_lunch_time = 11 <= (now_time + datetime.timedelta(hours=9)).hour < 13
    is_dinner_time = 17 <= (now_time + datetime.timedelta(hours=9)).hour < 19

    if is_lunch_time and not user.is_lunch:
        raise HTTPException(status_code=403, detail="Not lunch target")

    if is_dinner_time and not user.is_dinner:
        raise HTTPException(status_code=403, detail="Not dinner target")

    latest_qr = user.qr_list[-1]
    if latest_qr.authed_at is not None and (latest_qr.authed_at) > (now_time + datetime.timedelta(hours=2)):
        raise HTTPException(status_code=403, detail="Already Authed")

    code = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(10)])
    qr = Qr(code=code, user_id=user.id, created_at=datetime.datetime.now(datetime.timezone.utc))
    session.add(qr)
    user.qr_list.append(qr)
    session.commit()
    session.refresh(qr)

    return qr


@app.get("/api/qr/{code}")
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

    return qr.user


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
