"""
AI智能问答系统 - 后端服务入口
开发: uvicorn main:app --reload --port 8000
生产: python main.py
"""
# ⚠️ 必须在其他import之前加载.env
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base, SessionLocal
from app.routers import auth, chat, admin
from app import crud, models
import os
import sys

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化管理员账号
def init_admin():
    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_username(db, "admin")
        if not admin_user:
            admin_pwd = os.getenv("ADMIN_PASSWORD", "admin123456")
            crud.create_user(db, "admin", admin_pwd, is_admin=1)
            print("[系统] 管理员账号已初始化: admin /", admin_pwd)
        else:
            print("[系统] 管理员账号已存在")
    finally:
        db.close()

init_admin()

app = FastAPI(
    title="AI智能问答系统",
    description="大模型智能问答平台 - 基于 DeepSeek Anthropic API",
    version="1.0.0",
)

# CORS跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API路由（必须在静态文件之前注册，确保 /api 优先匹配）
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# 前端静态文件目录
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

if os.path.isdir(FRONTEND_DIR):
    # 托管 assets 目录（JS/CSS/图片等）
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # SPA 兜底：所有非 /api 请求返回 index.html
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str = ""):
        file_path = os.path.join(FRONTEND_DIR, full_path) if full_path else ""
        # 如果请求的是具体文件且存在，直接返回
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # 否则返回 index.html（Vue Router SPA 模式）
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/", summary="健康检查")
    def root():
        return {"message": "AI智能问答系统后端运行中", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    print(f"\n  AI智能问答系统")
    print(f"  |-- 后端API: http://{host}:{port}/api")
    print(f"  |-- API文档: http://{host}:{port}/docs")
    print(f"  |-- 前端页面: http://{host}:{port}/\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)

