from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from auth.security import hash_password, verify_password, create_token
from schemas.auth import UserRegister, UserLogin, TokenResponse

router=APIRouter(prefix="/auth")

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    user=User(
      username=data.username,
      email=data.email,
      password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token({"sub": user.username, "user_id": user.id})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_token({"sub": user.username, "user_id": user.id})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username
    )


@router.get("/search")
def search_users(q: str, db: Session = Depends(get_db)):
    """Search users by username or email"""
    users = db.query(User).filter(
        (User.username.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
    ).limit(10).all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email
        }
        for u in users
    ]


@router.get("/online")
def get_online_users():
    """Get list of online user IDs"""
    from websocket.manager import manager
    online_ids = manager.get_online_users()
    return {"online_users": list(online_ids)}