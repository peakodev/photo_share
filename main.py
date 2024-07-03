from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware


from app.routes import auth, users, posts, comments, tags, qrcode, admin
from front.routes import home

app = FastAPI()


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if 'X-Forwarded-Proto' in request.headers and request.headers['X-Forwarded-Proto'] == 'https':
            request.scope['scheme'] = 'https'
        response = await call_next(request)
        return response


app.add_middleware(HTTPSRedirectMiddleware)

home.router.app = app

app.mount("/static", StaticFiles(directory="front/static"), name="static")

# Serve Sphinx documentation
app.mount("/sphinx-docs", StaticFiles(directory="docs/build/html"), name="sphinx-docs")

# Code covarage
app.mount("/htmlcov", StaticFiles(directory="htmlcov"), name="htmlcov")


# Redirect from root to Sphinx documentation
@app.get("/help", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/sphinx-docs/index.html")


@app.get("/cov", include_in_schema=False)
async def redirect_to_htmlcov():
    return RedirectResponse(url="/htmlcov/index.html")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(qrcode.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(home.router, include_in_schema=False)


@app.get("/test")
def read_root():
    return {"Hello": "PHotoShare API is working!"}
