from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app import models, schemas, database, auth
from app.utils import send_password_reset_email 

auth_routes = APIRouter()

@auth_routes.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=False  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_routes.post("/login", response_model=schemas.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": db_user.username, "user_id": db_user.id, "is_admin": db_user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_routes.get("/verify")
def verify_token(current_user: models.User = Depends(auth.get_current_user)):
    """Verificar que el token sea válido y retornar info del usuario"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active
    }

@auth_routes.post("/password-recovery")
def recover_password(request: schemas.PasswordRecoveryRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_token = auth.create_access_token(data={"sub": user.email}) 
    send_password_reset_email(request.email, reset_token)  
    return {"message": "Password recovery email sent"}

@auth_routes.patch("/profile", response_model=schemas.UserResponse)
def update_profile(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user_update.username and not user_update.password:
        raise HTTPException(status_code=400, detail="At least one field must be provided for update")
    
    if user_update.username:
        db_user.username = user_update.username
        
    if user_update.password:
        db_user.hashed_password = auth.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@auth_routes.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):

    return current_user

@auth_routes.post("/register-admin", response_model=schemas.UserResponse)
def register_admin_user(
    user: schemas.UserCreateAdmin, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can create admin users")
    
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if existing_user:
        if existing_user.is_admin:
            raise HTTPException(status_code=400, detail="User is already an administrator")
        
        existing_user.is_admin = True
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    else:
        hashed_password = auth.get_password_hash(user.password)
        new_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_admin=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

@auth_routes.get("/users") 
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can view all users")
    
    query = db.query(models.User)
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    
    if role:
        if role == "admin":
            query = query.filter(models.User.is_admin == True)
        elif role == "user":
            query = query.filter(models.User.is_admin == False)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    users_data = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
        users_data.append(user_dict)
    
    return {
        "users": users_data,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@auth_routes.get("/users/stats")
def get_users_stats(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can view user stats")
    
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    admin_users = db.query(models.User).filter(models.User.is_admin == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "regular_users": total_users - admin_users
    }

@auth_routes.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Admin puede ver cualquier usuario, usuario regular solo su propia info
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
