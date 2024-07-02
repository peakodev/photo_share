from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.middlewares.middlewares import AuthMiddleware
from app.routes import auth, users, posts, comments, tags, qrcode, admin
from front.routes import home

app = FastAPI()

home.router.app = app

# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# app.add_middleware(AuthMiddleware)


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
