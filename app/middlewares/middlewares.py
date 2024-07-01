from typing import Optional
from fastapi import Request

from starlette.middleware.base import BaseHTTPMiddleware
from httpx import AsyncClient

from app.models.user import User
from app.services.auth import auth_service


# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):

#         token = request.headers.get("Authorization")
#         if token:
#             scheme, token = token.split()
#             if scheme.lower() == "bearer":
#                 # TODO заменить на httpx запрос /api/users
#                 user = await auth_service.get_current_user(request)
#                 if user:
#                     request.state.user = user
#         response = await call_next(request)
#         return response


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token:
            scheme, token = token.split()
            if scheme.lower() == "bearer":
                headers = {"Authorization": f"Bearer {token}"}
                async with AsyncClient() as client:
                    response = await client.get(
                        "http://localhost/api/users", headers=headers
                    )
                    if response.status_code == 200:
                        request.state.user = response.json()
        else:
            request.state.user = None

        response = await call_next(request)
        return response


# auth_service.get_current_user

# async def get_user_from_token(self, token: str, request: Request) -> Optional[User]:
#     db: AsyncSession = await get_db()(request)
#     try:
#         user_id = auth_service.decode_access_token(token)
#         stmt = select(User).where(User.id == user_id)
#         result = await db.execute(stmt)
#         user = result.scalars().first()
#         return user
#     except Exception as e:
#         return None
