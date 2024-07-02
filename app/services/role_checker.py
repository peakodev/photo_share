from fastapi import HTTPException, status, Depends

from app.models import Role, User
from app.services.auth import auth_service


def role_required(required_role: Role):
    """
    Decorator to check if the user has the required role

    Args:
        required_role (Role): Role required to access the route
    """
    def role_checker(current_user: User = Depends(auth_service.get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


moderator_required = role_required(Role.moderator)
admin_required = role_required(Role.admin)

# How to use modertor_required and admin_required:
#
# @router.get("/")
# async def get_users(current_user: User = Depends(moderator_required)):
#     return {"user": current_user}
#
# @router.get("/admin-endpoint", dependencies=[Depends(admin_required)])
# async def read_admin_endpoint():
#     return {"message": "Hello, Admin!"}
