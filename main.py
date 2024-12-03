import datetime
from typing import Annotated
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
    code: str
    created_at: datetime.datetime | None = Field(default=lambda: datetime.datetime.now(datetime.timezone.utc))
    authed_at: datetime.datetime | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    team: User | None = Relationship(back_populates="qr_list")


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

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


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


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
