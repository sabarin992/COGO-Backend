from fastapi import APIRouter,Request,Depends
from app.api.deps import get_current_user,get_current_admin
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.user import ResetPasswordRequest,EditProfile,UserResponse
from app.services import user_service
from fastapi import HTTPException, status
from app.core.exceptions import UserNotFoundError
from typing import List


router = APIRouter()





@router.get("/check-auth")
def check_auth(user=Depends(get_current_user)):
    return user


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


@router.get("/admin-users", response_model=List[UserResponse])
def get_all_users_except_admin(
    search: str | None = None,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    
    users = user_service.get_users_except_admin_service(db, search)
    return users


@router.patch("/admin/block/{user_id}", response_model=UserResponse)
def block_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return user_service.block_user_service(db, user_id)


@router.patch("/admin/unblock/{user_id}", response_model=UserResponse)
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db)

):
    return user_service.unblock_user_service(db, user_id)