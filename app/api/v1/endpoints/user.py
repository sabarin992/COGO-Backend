from fastapi import APIRouter,Request,Depends,Response
from app.api.deps import get_current_user,get_current_admin
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.user import ResetPasswordRequest,EditProfile,UserResponse,PaginatedUserResponse,EmailUpdateRequest,VerifyEmailUpdateRequest
from app.services import user_service
from fastapi import HTTPException, status
from app.core.exceptions import UserNotFoundError
from typing import List
from app.core.security import verify_token
from app.repositories import user_repo


router = APIRouter()





@router.get("/check-auth")
def check_auth(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # remove "Bearer " if added
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if payload is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = user_repo.get_user_by_email(db, email)
    if not user or user.is_blocked:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {"authenticated": True}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    
    user_service.reset_password(data,db)
    return {"message": "Password updated successfully"}




@router.get("/profile")
def profile(email=Depends(get_current_user), db: Session = Depends(get_db)):

    try:
        user = user_service.profile_service(db, email)
        return user

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    

@router.put("/edit-profile")
def edit_profile(
    data: EditProfile,
    db: Session = Depends(get_db),
    email=Depends(get_current_user)
):
    updated_user = user_service.edit_profile_service(db, email, data)

    return {
        "message": "Profile updated successfully",
        "user": updated_user
    }


@router.post("/request-email-update")
def request_email_update(
    data: EmailUpdateRequest,
    db: Session = Depends(get_db),
    current_user_email=Depends(get_current_user)
):
    user_service.request_email_update_service(db, current_user_email, data.new_email)
    return {"message": "OTP sent successfully"}


@router.post("/verify-email-update")
def verify_email_update(
    data: VerifyEmailUpdateRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user_email=Depends(get_current_user)
):
    updated_user = user_service.verify_email_update_service(
        db, current_user_email, data.new_email, data.otp, response
    )
    return {
        "message": "Email updated successfully",
        "user": updated_user
    }



@router.get("/admin-users", response_model=PaginatedUserResponse)
def get_all_users_except_admin(
    search: str | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 5,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    
    return user_service.get_users_except_admin_service(db, search, status, page, size)


@router.patch("/admin/block/{user_id}", response_model=UserResponse)
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return user_service.block_user_service(db, user_id)


@router.patch("/admin/unblock/{user_id}", response_model=UserResponse)
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return user_service.unblock_user_service(db, user_id)