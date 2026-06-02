"""
模型参数配置模块 + .env 文件读写
"""
import os

# ─── 环境变量读取 ───
AI_API_URL = os.getenv("AI_API_URL", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "DeepSeek-V4-pro")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))
AI_SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT", "你是一个智能助手，请用简洁友好的方式回答用户的问题。")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123456")

SECRET_KEY = os.getenv("SECRET_KEY", "ai-chat-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ─── .env 文件读写 ───
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

AI_CONFIG_KEYS = [
    "AI_API_URL",
    "AI_API_KEY",
    "AI_MODEL",
    "AI_TEMPERATURE",
    "AI_MAX_TOKENS",
    "AI_SYSTEM_PROMPT",
]

def read_env_config() -> dict:
    """读取 .env 中 AI 相关配置"""
    result = {k: "" for k in AI_CONFIG_KEYS}
    if not os.path.isfile(ENV_FILE):
        return result
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            if key in result:
                result[key] = val.strip()
    return result


def write_env_config(updates: dict) -> dict:
    """将 AI 配置写入 .env 并同步更新当前进程环境变量"""
    if not os.path.isfile(ENV_FILE):
        return {"error": ".env 文件不存在"}

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated = set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in updates:
            lines[i] = f"{key}={updates[key]}\n"
            updated.add(key)

    # 追加 .env 中不存在的新 key
    for key, val in updates.items():
        if key not in updated and key in AI_CONFIG_KEYS:
            lines.append(f"{key}={val}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # 同步更新当前进程环境变量（立即生效，无需重启）
    for key, val in updates.items():
        os.environ[key] = val
    # 刷新模块级别的引用
    _reload_env_vars()

    return read_env_config()


def _reload_env_vars():
    """刷新模块级变量（配置更改后调用）"""
    global AI_API_URL, AI_API_KEY, AI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS, AI_SYSTEM_PROMPT
    AI_API_URL = os.getenv("AI_API_URL", "")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "DeepSeek-V4-pro")
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))
    AI_SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT", "你是一个智能助手，请用简洁友好的方式回答用户的问题。")
