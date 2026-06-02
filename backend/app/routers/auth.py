"""用户认证路由 - 注册、登录、用户信息、管理员管理"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import crud, schemas, auth, database, models

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=schemas.Token, summary="用户注册")
def register(data: schemas.UserRegister, db: Session = Depends(database.get_db)):
    """新用户注册，成功后自动登录返回Token"""
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if data.email:
        existing = db.query(models.User).filter(models.User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="该邮箱已被注册")
    user = crud.create_user(db, data.username, data.password, data.email)
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token, summary="用户登录")
def login(data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """用户登录，验证后返回Token"""
    user = crud.get_user_by_username(db, data.username)
    if not user or not crud.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserInfo, summary="获取当前用户信息")
def get_user_info(current_user: models.User = Depends(auth.get_current_user)):
    """获取当前登录用户的基本信息"""
    return schemas.UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
    )


# ─── 管理员接口 ───

@router.get("/admin/users", response_model=schemas.AdminUserList, summary="管理员-用户列表")
def admin_get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    keyword: str = Query(None, description="搜索关键词"),
    admin: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(database.get_db),
):
    """管理员获取所有用户列表（支持搜索）"""
    total, users = crud.get_all_users_paginated(db, page, page_size, keyword)
    user_list = [
        schemas.UserInfo(
            id=u.id,
            username=u.username,
            email=u.email,
            created_at=u.created_at,
        )
        for u in users
    ]
    return {"total": total, "page": page, "page_size": page_size, "records": user_list}


@router.get("/admin/check", summary="检查是否管理员")
def check_admin(current_user: models.User = Depends(auth.get_current_user)):
    """检查当前用户是否为管理员"""
    return {"is_admin": current_user.is_admin == 1, "username": current_user.username}
