from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.conf.config import templates

# templates = Jinja2Templates(directory="frontend/templates")
# router = APIRouter(prefix="/home", tags=["home"])
router = APIRouter()
# router = app


@router.get(
    "/",
    # response_model=list[PostResponse],
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    name="home_page"
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
