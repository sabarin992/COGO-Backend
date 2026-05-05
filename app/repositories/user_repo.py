from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()


def create_user(db: Session, user_data: dict):
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_user_by_email(db,user):
    user.email_verified = True
    db.commit()
    db.refresh(user)  



def get_or_create_user(db: Session, email: str, name: str):

    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    new_user = User(
    email=email,
    full_name=name,   
    role="consumer"  
)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def edit_user_profile(db, user, data):
    user.full_name = data.full_name
    user.phone = data.phone

    db.commit()
    db.refresh(user)

    return user