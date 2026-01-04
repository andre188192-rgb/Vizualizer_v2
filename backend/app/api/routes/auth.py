from fastapi import APIRouter, Depends

from ...core.security import create_access_token, get_current_user

router = APIRouter()


@router.post("/auth/token")
async def issue_token(user: str = Depends(get_current_user)) -> dict:
    token = create_access_token(subject=user, role="ui")
    return {"access_token": token, "token_type": "bearer"}
