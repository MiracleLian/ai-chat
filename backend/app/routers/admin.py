"""管理员配置路由 - 登录返回 JWT，读写 AI 配置需 Token"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from ..config import (
    ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY, ALGORITHM,
    read_env_config, write_env_config, AI_CONFIG_KEYS,
)
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/admin", tags=["管理员配置"])

admin_bearer = HTTPBearer(auto_error=False)


def create_admin_token() -> str:
    """生成管理员 JWT（有效期 2 小时）"""
    expire = datetime.now(timezone.utc) + timedelta(hours=2)
    payload = {"sub": "admin", "admin": True, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_bearer),
) -> bool:
    """验证管理员 Token 依赖"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="需要管理员 Token")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("admin"):
            raise HTTPException(status_code=403, detail="需要管理员权限")
    except JWTError:
        raise HTTPException(status_code=401, detail="管理员 Token 无效或已过期")
    return True


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class ConfigUpdateRequest(BaseModel):
    """AI 配置更新请求，所有字段可选"""
    AI_API_URL: str | None = None
    AI_API_KEY: str | None = None
    AI_MODEL: str | None = None
    AI_TEMPERATURE: float | None = None
    AI_MAX_TOKENS: int | None = None
    AI_SYSTEM_PROMPT: str | None = None


@router.post("/login", summary="管理员登录")
def admin_login(body: AdminLoginRequest):
    """验证管理员账号密码，成功返回 JWT Token"""
    if body.username != ADMIN_USERNAME or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="管理员账号或密码错误")
    token = create_admin_token()
    return {"access_token": token, "token_type": "bearer", "admin": True}


@router.get("/config", summary="获取 AI 配置")
def get_config(_: bool = Depends(verify_admin_token)):
    """读取当前 .env 中的 AI 配置（敏感信息部分隐藏）"""
    cfg = read_env_config()
    key = cfg.get("AI_API_KEY", "")
    if key and len(key) > 8:
        cfg["AI_API_KEY"] = key[:4] + "****" + key[-4:]
    elif key and len(key) <= 8:
        cfg["AI_API_KEY"] = key[:2] + "****"
    return cfg


@router.put("/config", summary="更新 AI 配置")
def update_config(body: ConfigUpdateRequest, _: bool = Depends(verify_admin_token)):
    """更新 .env 中的 AI 配置项，立即生效"""
    updates = {}
    for key in AI_CONFIG_KEYS:
        val = getattr(body, key, None)
        if val is not None:
            updates[key] = str(val)

    if not updates:
        raise HTTPException(status_code=400, detail="没有要更新的配置项")

    result = write_env_config(updates)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {"success": True, "message": "配置已更新，立即生效", "config": result}
