from typing import Annotated, Optional
import httpx

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from httpx import AsyncClient

from app.middlewares.middlewares import AuthMiddleware
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


async def get_user_from_request(request: Request) -> Optional[User]:
    from main import app

    token = request.headers.get("Authorization")
    user = None
    if token:
        scheme, token = token.split()
        if scheme.lower() == "bearer":
            headers = {"authorization": f"Bearer {token}"}
            api_path = app.url_path_for("get_user")
            api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"

            print(f'"!!!!!!!!!!  {request.headers=}"')
            print(f'"!!!!!!!!!!  {headers=}"')

            async with AsyncClient() as client:
                response = await client.get(api_url, headers=headers)
                response_json = response.json()
                print(f"!!!!!!!!!!  {response_json=}")
                if response.status_code == 200:
                    user = User(**response_json)
    return user


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
    user: Optional[User] = Depends(get_user_from_request),
):
    from main import app

    api_path = app.url_path_for("get_posts")
    api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    else:
        headers = request.headers

    print(f"***** /my_posts --- {user.id=} {user.first_name=} {user.email=}")
    print(f"***** /my_posts --- {api_url=}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
    except Exception as err:
        print(f"##### Exception {err=}")
        ...

    if response.status_code != 200:
        return templates.TemplateResponse(
            request=request,
            name="posts_my.html",
            context={
                "request": request,
                "message": response,
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="posts_my.html",
        context={
            "request": request,
            "posts": response.json(),
            "user": user,
            "is_user": True if user else False,
        },
    )


@router.get(
    "/posts",
    name="posts_page",
    response_class=HTMLResponse,
)
async def get_all_posts_page(
    request: Request,
    token: Optional[str] = Depends(get_token_optional),
    user: Optional[User] = Depends(get_user_from_request),
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
            context={
                "request": request,
                "message": response,
                "user": user,
                "is_user": True if user else False,
            },
        )

    # await log_response(response)
    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={"request": request, "posts": response.json()},
    )


@router.get(
    "/post_create",
    name="posts_create_page",
    response_class=HTMLResponse,
)
async def get_create_post_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="post_create.html",
        context={
            "request": request,
        },
    )


@router.post(
    "/post_create",
    name="posts_create_page",
    response_class=HTMLResponse,
)
async def post_create_post_page(
    request: Request,
    description: str = Form(),
    tags: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    user: Optional[User] = Depends(get_user_from_request),
    # token: Optional[str] = Depends(get_token_optional),
):
    print("@@@@@@@")
    from main import app

    print(f"{request.headers}")
    headers = {}
    is_token = False
    if "authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]
        is_token = True

    if is_token:
        print(f'request.url_for("create_post"): {request.url_for("create_post")}')
        api_path = app.url_path_for("create_post")
        api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"

        api_url = str(request.url_for("create_post"))
        print(f"______ {api_url=}")
        print(f"______ {str(api_url)=}")

        file_content = await photo.read()

        params = {"description": description, "tags": tags}
        file = {"file": (photo.filename, file_content, photo.content_type)}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url, params=params, files=file, headers=headers
            )
        print(f"{response.status_code=}")
        if response.status_code != 201:
            print(f"create error:{response.status_code=}")
            return templates.TemplateResponse(
                request=request,
                name="post_create.html",
                context={"request": request, "message": response},
            )
        combined_response = {**response.json(), "detail": "Post created succesfully"}

    return templates.TemplateResponse(
        request=request,
        name="post_id.html",
        context={"request": request, "post": combined_response},
    )


@router.get(
    "/posts/{post_id}",
    name="post_id_page",
)
async def get_post_page(
    post_id: int,
    request: Request,
    user: Optional[User] = Depends(get_user_from_request),
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
        context={
            "request": request,
            "post": response.json(),
            "user": user,
            "is_user": True if user else False,
        },
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
