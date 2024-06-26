from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Depends,
    Request,
    UploadFile,
    status,
    Query,
)

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models import User, get_db
from app.schemas.post import (
    PostResponse,
    PostCreateResponse,
    PostDeleteSchema,
)
from app.repository import posts as repository_posts
from app.services.auth import auth_service
from app.services.cloudinary import Effect, upload_photo, transform_photo

from app.conf.config import templates


router = APIRouter(prefix="/posts", tags=["posts"])


# access_to_route_all = RoleAccess([Role.ADMIN])


@router.get(
    "/",
    response_model=list[PostResponse],
    name="posts_page",
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def get_posts(
    limit: int = Query(10),
    offset: int = Query(0),
    request=Request,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    print("get_posts")
    posts = await repository_posts.get_posts(limit, offset, user, db)
    return posts
    # return templates.TemplateResponse(
    #     request=request, name="home.html", context={"request": request, "posts": posts}
    # )


@router.get(
    "/all",
    response_model=list[PostResponse],
    dependencies=[
        # Depends(access_to_route_all),
        # Depends(RateLimiter(times=1, seconds=10)),
    ],
)
async def get_all_posts(
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    posts = await repository_posts.get_all_posts(limit, offset, db)
    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    post = await repository_posts.get_post(post_id, user, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get(
    "/find/",
    response_model=list[PostResponse],
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def find_post(
    find_str: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    posts = await repository_posts.find_posts(find_str, user, db)
    if len(posts) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=" Post not found"
        )
    return posts


@router.post(
    "/create",
    response_model=PostCreateResponse,
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    description: str,
    tags: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    # photo_url = cloudinary_upload(file, user.id)

    new_post = await repository_posts.create_post(description, tags, file, user, db)

    return new_post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def update_post(
    post_id: int,
    description: str = None,
    tags: str = None,
    effect: str = None,
    file: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    post = await repository_posts.update_post(
        post_id, user, db, description, tags, effect, file
    )
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


@router.delete(
    "/{post_id}",
    response_model=PostDeleteSchema,
    # dependencies=[Depends(RateLimiter(times=1, seconds=10))],
)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    post = await repository_posts.delete_post(post_id, user, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post
