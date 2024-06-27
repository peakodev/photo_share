from typing import Annotated
import httpx
from pydantic import BaseModel
import requests
from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models.user import User
from app.schemas.user import TokenModel
from app.services.auth import auth_service

from app.schemas.user import UserModel, UserResponse, TokenModel, RequestEmail
from sqlalchemy.orm import Session

# app = FastAPI()

router = APIRouter()
templates = Jinja2Templates(directory="front/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.get(
    "/",
    # response_model=list[PostResponse],
    # response_model=TokenModel,
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    name="home_page",
)
def get_home(
    request: Request,
    # body: OAuth2PasswordRequestForm = Depends(),
    # db: Session = Depends(get_db),
    # user: User = Depends(auth_service.get_current_user) ,
):
    # print(f"request = {request}")
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={},
    )
    # return templates.TemplateResponse("home.html")
    # return {"Hello": "World"}


@router.get(
    "/my_posts",
    name="my_posts_page",
    response_class=HTMLResponse,
    # response_model=TokenModel,
)
def get_my_posts(
    request: Request,
    token: str = Depends(oauth2_scheme),
    # db: Session = Depends(get_db),
    # user: User = Depends(auth_service.get_current_user),
):
    # print(f"#R-get_my_posts --- Received token: {token}")
    from main import app

    api_path = app.url_path_for("get_posts")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"#R-get_my_posts --- Requesting URL: {api_url}")
    print(f"#R-get_my_posts --- Headers: {headers}")

    response = requests.get(api_url, headers=headers)
    res = response.json()
    print(f"#R-get_my_posts --- recived posts")
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch posts"
        )

    return templates.TemplateResponse(
        request=request,
        name="posts_my.html",
        context={"request": request, "token": token, "posts": res},
    )
    # return templates.TemplateResponse("home.html")
    # return {"Hello": "World"}


@router.get(
    "/posts",
    name="posts_page",
    response_class=HTMLResponse,
    # response_model=TokenModel,
)
def get_all_posts(
    request: Request,
    token: str = Depends(oauth2_scheme),
):
    from main import app

    api_path = app.url_path_for("get_all_posts")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"
    headers = {"Authorization": f"Bearer {token}"}

    # print(f"#R-get_my_posts --- Requesting URL: {api_url}")
    # print(f"#R-get_my_posts --- Headers: {headers}")

    response = requests.get(api_url, headers=headers)
    res = response.json()
    # print(f"#R-get_my_posts --- recived posts")
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch posts"
        )

    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={"request": request, "token": token, "posts": res},
    )
    # return templates.TemplateResponse("home.html")
    # return {"Hello": "World"}


@router.get("/signup", name="signup_page")
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signup.html", context={"request": request}
    )


# class UserSignupFormSchema(BaseModel):
#     # first_name: str = Annotated[str, Form()]
#     # last_name = (Form(),)
#     email: Annotated[str, Form()]
#     # email: str = (Form(),)
#     # password = (Form(),)


@router.post(
    "/signup",
    name="signup_post_page",
    response_model=UserResponse,
)
async def fe_signup(
    request: Request,
    firstname: Annotated[str, Form()],
    lastname: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    from main import app

    form_data = {
        "first_name": firstname,
        "last_name": lastname,
        "email": email,
        "password": password,
    }
    # print("!!!!!!! formdata", email)
    print("!!!!!!! formdata", form_data)

    api_path = app.url_path_for("auth_post_signup")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"
    api_url = "http://localhost:8000/api/auth/signup"
    print(f"{api_url=}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=form_data)
    except Exception as err:
        print("!!!!! error", err)
        return {"err": err}
    print(f"{response=}")
    # response = requests.post(api_url, json=form_data)
    if response.status_code != 201:
        # response_json = response.json()
        print(
            f"!#F_Route - ERROR - signup user, res: \
                \n {response.status_code=}\
                \n {response.reason_phrase=}\
                \n {response.json()=}\
                \n {response.content=}\
                \n {response.text=}\
                \n {response=}"
        )

        return templates.TemplateResponse(
            request=request,
            name="auth/signup.html",
            context={"request": request, "message": response},
        )
        # TODO изменить на возврат авторизации с Message
        raise HTTPException(
            status_code=response.status_code, detail="Failed to fetch posts"
        )
    print("@@@@@@@@@@@@@@@@@@@@@@")
    # return {"response": response}
    # redirect_url = request.app.url_path_for("signin_page")
    redirect_url = request.app.url_path_for("home_page")
    # return RedirectResponse(url=redirect_url, status_code=303)
    # return {"user": new_user, "detail": "User successfully created"}
    # return {"user": response.user, "detail": response.detail}
    return templates.TemplateResponse(
        request=request,
        name="auth/signup.html",
        context={"request": request, "message": response},
        )


async def signup_post_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signup.html", context={"request": request}
    )


@router.get("/signin", name="signin_page")
async def signin_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signin.html", context={"request": request}
    )
