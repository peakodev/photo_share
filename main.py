from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import auth, users, posts, comments, tags, qrcode, admin
from front.routes import home

app = FastAPI()

app.mount("/static", StaticFiles(directory="front/static"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(qrcode.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(home.router)


@app.get("/test")
def read_root():
    return {"Hello": "PHotoShare API is working!"}
