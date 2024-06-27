from typing import Optional
from fastapi import Request

from fastapi.middleware.base import BaseHTTPMiddleware

from app.models.user import User

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        # token = request.headers.get("Authorization")
        # if token:
        #     scheme, token = token.split()
        #     if scheme.lower() == 'bearer':
        #         user = await self.get_user_from_token(token, request)
        #         if user:
        #             request.state.user = user
        response = await call_next(request)
        return response


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