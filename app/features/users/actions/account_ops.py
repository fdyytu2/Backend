from fastapi import HTTPException
from app.core.hashing import verify_password
from app.features.users.actions.profile import get_user_profile

def terminate_user_account(db, user_id: str, password: str):
    user = get_user_profile(db, user_id)
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Password salah")
    db.delete(user)
    db.commit()
