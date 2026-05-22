from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()

# Fetch user using id
def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()


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


# get all user except admin
def get_all_users_except_admin(
    db: Session, 
    search: str | None = None, 
    status: str | None = None,
    page: int = 1,
    size: int = 5
):
    query = db.query(User).filter(User.role != "admin")
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.phone.ilike(search_filter))
        )
    if status:
        if status == "Active":
            query = query.filter(User.is_blocked == False)
        elif status == "Blocked":
            query = query.filter(User.is_blocked == True)
        elif status == "Pending":
            query = query.filter(User.id == -1)
            
    total = query.count()
    offset = (page - 1) * size
    users = query.offset(offset).limit(size).all()
    return users, total


# block or unblock user
def update_user_block_status(db, user, status):
    user.is_blocked = status
    db.commit()
    db.refresh(user)
    return user