from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── 用户操作 ───

def get_user_by_username(db: Session, username: str):
    """根据用户名查询用户"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """根据ID查询用户"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, username: str, password: str, email: str = None, is_admin: int = 0):
    """创建新用户"""
    hashed = pwd_context.hash(password)
    user = models.User(username=username, hashed_password=hashed, email=email, is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain, hashed)


def change_password(db: Session, user: models.User, new_password: str):
    """修改密码"""
    user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(user)
    return user


# ─── 管理员 — 用户管理 ───

def get_all_users_paginated(db: Session, page: int = 1, page_size: int = 10, keyword: str = None):
    """管理员分页获取所有用户（可搜索）"""
    query = db.query(models.User)
    if keyword:
        query = query.filter(
            models.User.username.contains(keyword) |
            (models.User.email.contains(keyword) if models.User.email is not None else False)
        )
    total = query.count()
    users = (
        query.order_by(models.User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, users


# ─── 对话操作 ───

def create_chat(db: Session, user_id: int, question: str, answer: str):
    """创建对话记录"""
    record = models.ChatRecord(user_id=user_id, question=question, answer=answer)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_chat_by_id(db: Session, chat_id: int, user_id: int):
    """获取单条对话记录（需属于当前用户）"""
    return (
        db.query(models.ChatRecord)
        .filter(models.ChatRecord.id == chat_id, models.ChatRecord.user_id == user_id)
        .first()
    )


def get_chats_paginated(db: Session, user_id: int, page: int = 1, page_size: int = 10):
    """分页获取对话历史"""
    query = db.query(models.ChatRecord).filter(models.ChatRecord.user_id == user_id)
    total = query.count()
    records = (
        query.order_by(models.ChatRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, records


def get_user_chat_count(db: Session, user_id: int) -> int:
    """获取用户对话总数"""
    return db.query(func.count(models.ChatRecord.id)).filter(
        models.ChatRecord.user_id == user_id
    ).scalar() or 0


def delete_chat(db: Session, chat_id: int, user_id: int):
    """删除对话记录"""
    record = get_chat_by_id(db, chat_id, user_id)
    if record:
        db.delete(record)
        db.commit()
    return record


def delete_chats_batch(db: Session, chat_ids: list[int], user_id: int):
    """批量删除对话记录"""
    deleted = 0
    for cid in chat_ids:
        record = get_chat_by_id(db, cid, user_id)
        if record:
            db.delete(record)
            deleted += 1
    db.commit()
    return deleted
