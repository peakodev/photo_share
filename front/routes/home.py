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
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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
                    "message": response.json(),
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
    else:
        print("_______ Not user and token")
        return templates.TemplateResponse(
            request=request,
            name="posts_my.html",
            context={
                "request": request,
                "message": {"detail": "Not authorized"},
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
    "/post",
    name="post_create_page",
    response_class=HTMLResponse,
)
async def get_create_post_page(
    request: Request,
    user: Optional[User] = Depends(get_user_from_request),
):

    return templates.TemplateResponse(
        request=request,
        name="post_create.html",
        context={"request": request, "user": user},
    )


@router.post(
    "/post",
    name="post_create_page",
    # response_class=HTMLResponse,
)
async def post_create_post_page(
    request: Request,
    description: str = Form(),
    tags: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    user: Optional[User] = Depends(get_user_from_request),
):
    print("@@@@@@@ Post CREATE PAGE")
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
        # print(f"______ {api_url=}")
        print(f"______ {str(api_url)=}")

        file_content = await photo.read()

        params = {"description": description, "tags": tags}
        file = {"file": (photo.filename, file_content, photo.content_type)}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url, params=params, files=file, headers=headers
            )

        # print(f"{response.status_code=}")
        response_json_py = response.json()
        # print(f"+++++++++ {response_json_py=}")
        if response.status_code != 201:
            print(f"create error:{response.status_code=}")
            return templates.TemplateResponse(
                request=request,
                name="post_create.html",
                context={"request": request, "message": response_json_py},
            )
        print("Return ")
        return JSONResponse(
            content=response_json_py, status_code=status.HTTP_201_CREATED
        )
    return templates.TemplateResponse(
        request=request,
        name="post_id.html",
        context={
            "request": request,
            "post": response_json_py,
            "message": {"detail": "Not authorized"},
            "user": user,
        },
    )


@router.put(
    "/post/{post_id}",
    name="posts_update_page",
    # response_class=HTMLResponse,
)
async def post_update_post_page(
    request: Request,
    post_id: int,
    description: str = Form(),
    tags: Optional[str] = Form(None),
    photo: UploadFile = File(default=None),
    user: Optional[User] = Depends(get_user_from_request),
):
    print("@@@@@@@ Post UPDATE PAGE")
    from main import app

    print(f"{request.headers}")
    headers = {}
    is_token = False
    if "authorization" in request.headers:
        headers["Authorization"] = request.headers["Authorization"]
        is_token = True

    if is_token:
        print(
            f'request.url_for("update_post"): {request.url_for("update_post", post_id=post_id)}'
        )
        api_path = app.url_path_for("update_post", post_id=post_id)
        api_url = f"{request.url.scheme}://{request.url.netloc}{api_path}"

        api_url = str(request.url_for("update_post", post_id=post_id))
        # print(f"______ {api_url=}")
        # print(f"______ {str(api_url)=}")

        # if photo is None and photo.filename:
        if True:
            print(f"############# file {photo}")
            file_content = await photo.read()
            params = {"description": description, "tags": tags}
            file = {"file": (photo.filename, file_content, photo.content_type)}
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    api_url, params=params, files=file, headers=headers
                )

        print(f"{response.status_code=}")
        response_json_py = response.json()
        print(f"+++++++++ {response_json_py=}")
        if response.status_code != 200:
            print(f"create error:{response.status_code=}")
            return templates.TemplateResponse(
                request=request,
                name="post_create.html",
                context={"request": request, "message": response_json_py},
            )
        print("Return ")
        return JSONResponse(content=response_json_py, status_code=status.HTTP_200_OK)
    return templates.TemplateResponse(
        request=request,
        name="post_id.html",
        context={
            "request": request,
            "post": response_json_py,
            "message": {"detail": "Post not update, need authorization"},
            "user": user,
        },
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


@router.get("/signup", name="signup_page")
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signup.html", context={"request": request}
    )


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
    if response.status_code != 201:
        return templates.TemplateResponse(
            request=request,
            name="auth/signup.html",
            context={"request": request, "message": response},
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


@router.get("/signin", name="signin_page")
async def signin_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signin.html", context={"request": request}
    )
