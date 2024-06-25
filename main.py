from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import auth, users, posts, comments, tags, qrcode, home

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(qrcode.router, prefix="/api")
app.include_router(home.router)

# app.add_api_router()


# @app.get("/")
# def read_root(request: Request):
# return RedirectResponse(url="/home")
# return templates.TemplateResponse(
#     request=request, name="home.html", context={"request": request}
# )
# return {"Hello": "World"}
