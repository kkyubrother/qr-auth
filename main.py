from fastapi import FastAPI
from qr_auth.routers import qr, user, bot, admin


app = FastAPI()

app.include_router(qr.router)
app.include_router(user.router)
app.include_router(bot.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

