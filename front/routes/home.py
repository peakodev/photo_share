from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="front/templates")


@router.get(
    "/",
    # response_model=list[PostResponse],
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    name="home_page",
)
def get_home(
    request: Request,
    # db: Session = Depends(get_db),
    # user: User = Depends(auth_service.get_current_user),
):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"request": request}
    )
    # return templates.TemplateResponse("home.html")
    # return {"Hello": "World"}


@router.get(
    "/my_posts",
    name="my_posts_page",
)
def get_my_posts(
    request: Request,
    # db: Session = Depends(get_db),
    # user: User = Depends(auth_service.get_current_user),
):
    return templates.TemplateResponse(
        request=request, name="posts_my.html", context={"request": request}
    )
    # return templates.TemplateResponse("home.html")
    # return {"Hello": "World"}


@router.get("/signup", name="signup_page")
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signup.html", context={"request": request}
    )
    
    
    
@router.get("/signin", name="signin_page")
async def signin_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth/signin.html", context={"request": request}
    )