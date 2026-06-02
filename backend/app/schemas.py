from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# ─── 用户相关 ───

class UserRegister(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 6 or len(v) > 20:
            raise ValueError("用户名长度需为6-20位")
        if not v.isalnum():
            raise ValueError("用户名只能包含字母和数字")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码长度需为8-20位")
        has_alpha = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_alpha and has_digit):
            raise ValueError("密码需包含字母和数字")
        return v


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── 对话相关 ───

class ChatCreate(BaseModel):
    """发送问题请求"""
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("问题不能为空")
        if len(v) > 2000:
            raise ValueError("问题长度不能超过2000字符")
        return v


class ChatOut(BaseModel):
    """对话记录响应"""
    id: int
    question: str
    answer: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatHistoryOut(BaseModel):
    """分页对话历史响应"""
    total: int
    page: int
    page_size: int
    records: list[ChatOut]


class AdminUserList(BaseModel):
    """管理员用户列表响应"""
    total: int
    page: int
    page_size: int
    records: list[UserInfo]
