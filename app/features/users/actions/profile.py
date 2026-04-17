from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.features.users.repository import UserRepository

def get_user_profile(db, user_id: str):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user_profile(db, user_id: str, username: str = None, email: str = None):
    repo = UserRepository(db)
    user = get_user_profile(db, user_id)

    if username:
        username_norm = username.strip()
        if username_norm and username_norm != user.username:
            if repo.get_by_username(username_norm):
                raise HTTPException(status_code=400, detail="Username already used")
            user.username = username_norm

    if email is not None:
        email_norm = email.strip().lower()
        if email_norm == "":
            user.email, user.email_verified = None, False
        elif email_norm != (user.email or ""):
            if repo.get_by_email(email_norm):
                raise HTTPException(status_code=400, detail="Email already used")
            user.email, user.email_verified = email_norm, False

    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed: Conflict")
