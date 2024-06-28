from typing import Annotated, Optional
import httpx

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.models.user import User
from app.schemas.post import PostResponse
from app.schemas.user import TokenModel
from app.services.auth import auth_service

from app.schemas.user import UserModel, UserResponse, TokenModel, RequestEmail

# app = FastAPI()

router = APIRouter()
templates = Jinja2Templates(directory="front/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
# oauth2_scheme = OAuth2PasswordBearer()


async def get_token_optional(request: Request) -> Optional[str]:
    authorization: str = request.headers.get("Authorization")
    if authorization:
        scheme, token = authorization.split()
        if scheme.lower() == "bearer":
            return token
    return None


async def log_response(response):
    print(
        f"!#F_Route - ERROR - signup user, res: \
        \n {response.status_code=}\
        \n {response.reason_phrase=}\
        \n {response.json()=}\
        \n {response.content=}\
        \n {response.text=}\
        \n {response=}"
    )


@router.get(
    "/",
    name="home_page",
)
def get_home(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={},
    )


@router.get(
    "/my_posts",
    name="my_posts_page",
    response_class=HTMLResponse,
)
async def get_my_posts_page(
    request: Request,
    token: Optional[str] = Depends(get_token_optional),
):
    from main import app

    api_path = app.url_path_for("get_posts")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    else:
        headers = request.headers

    # print(f"#R-get_my_posts --- Requesting URL: {api_url}")
    # print(f"#R-get_my_posts --- Headers: {headers}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
    except Exception as err:
        print(f"##### Exception {err=}")
        ...
    # print(f"#R-get_my_posts --- recived posts")

    if response.status_code != 200:
        return templates.TemplateResponse(
            request=request,
            name="posts_my.html",
            context={"request": request, "message": response},
        )

    return templates.TemplateResponse(
        request=request,
        name="posts_my.html",
        context={"request": request, "posts": response.json()},
    )


@router.get(
    "/posts",
    name="posts_page",
    response_class=HTMLResponse,
)
async def get_all_posts_page(
    request: Request,
    token: Optional[str] = Depends(get_token_optional),
):
    from main import app

    api_path = app.url_path_for("get_all_posts")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"

    if token:
        headers = {"Authorization": f"Bearer {token}"}
    else:
        headers = request.headers

    # print(f"#R-get_my_posts --- Requesting URL: {api_url}")
    # print(f"#R-get_my_posts --- Headers: {headers}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
    except Exception as err:
        print("!!!!! error", err)
        return {"err": err}

    print(f"{response=}")
    if response.status_code != 200:
        return templates.TemplateResponse(
            request=request,
            name="posts.html",
            context={"request": request, "message": response},
        )

    # await log_response(response)
    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={"request": request, "posts": response.json()},
    )


@router.get(
    "/posts/{post_id}",
    # response_model=PostResponse,
    name="post_id_page",
)
async def get_post_page(
    post_id: int,
    request: Request,
    # user: User = Depends(auth_service.get_current_user),
):
    from main import app

    # print(f"{request.headers}")
    print(f"{post_id=}")
    api_path = app.url_path_for("get_post_by_id", post_id=post_id)
    print(f"{api_path=}")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=request.headers)
    except Exception as err:
        print("!!!!! error", err)
        return {"err": err}

    if response.status_code != 200:
        return templates.TemplateResponse(
            request=request,
            name="post_id.html",
            context={"request": request, "message": response},
        )

    return templates.TemplateResponse(
        request=request,
        name="post_id.html",
        context={"request": request, "post": response.json()},
    )

    # return f"{request.headers}"


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
