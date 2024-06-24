from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routes import auth, users, posts, comments, tags, qrcode

app = FastAPI()


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(qrcode.router, prefix="/api")


@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")
