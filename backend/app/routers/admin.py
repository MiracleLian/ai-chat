"""管理员配置路由 - 登录、读取/修改 AI 配置"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import (
    ADMIN_USERNAME, ADMIN_PASSWORD,
    read_env_config, write_env_config, AI_CONFIG_KEYS,
)

router = APIRouter(prefix="/admin", tags=["管理员配置"])


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
    """验证管理员账号密码，成功返回临时管理 Token"""
    if body.username != ADMIN_USERNAME or body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="管理员账号或密码错误")
    return {"success": True, "message": "验证成功", "admin": True}


@router.get("/config", summary="获取 AI 配置")
def get_config():
    """读取当前 .env 中的 AI 配置（敏感信息部分隐藏）"""
    cfg = read_env_config()
    # 对 API Key 做部分隐藏
    key = cfg.get("AI_API_KEY", "")
    if key and len(key) > 8:
        cfg["AI_API_KEY"] = key[:4] + "****" + key[-4:]
    if key and len(key) <= 8:
        cfg["AI_API_KEY"] = key[:2] + "****"
    return cfg


@router.put("/config", summary="更新 AI 配置")
def update_config(body: ConfigUpdateRequest):
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
