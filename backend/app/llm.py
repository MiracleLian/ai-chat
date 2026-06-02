"""
大模型调用模块 - 支持Anthropic Messages API兼容接口
可对接：DeepSeek Anthropic API 等平台
配置值在每次调用时从 config 模块动态读取，支持热更新。
"""
import httpx
import os
import json
from . import config


def _get_config():
    """每次调用时重新读取，确保管理员修改后立即生效"""
    return {
        "url": config.AI_API_URL,
        "key": config.AI_API_KEY,
        "model": config.AI_MODEL,
        "temperature": config.AI_TEMPERATURE,
        "max_tokens": config.AI_MAX_TOKENS,
        "system": config.AI_SYSTEM_PROMPT,
    }


async def call_llm(question: str) -> str:
    """
    调用大语言模型获取回答（Anthropic Messages API格式）
    如果未配置API，返回模拟回答
    """
    cfg = _get_config()
    if not cfg["url"] or not cfg["key"]:
        return f"[模拟回答] 你问的是：{question}\n\n这是模拟回复，请在 .env 文件中配置 AI_API_URL 和 AI_API_KEY 以启用真实AI对话。"

    try:
        headers = {
            "x-api-key": cfg["key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": cfg["model"],
            "max_tokens": cfg["max_tokens"],
            "temperature": cfg["temperature"],
            "system": cfg["system"],
            "messages": [
                {"role": "user", "content": question},
            ],
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(cfg["url"], headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Anthropic格式返回：content是数组，提取text类型的内容
            if "content" in data and isinstance(data["content"], list):
                text_parts = []
                for block in data["content"]:
                    if block.get("type") == "text":
                        text_parts.append(block["text"])
                if text_parts:
                    return "\n".join(text_parts)

            return json.dumps(data, ensure_ascii=False)

    except httpx.TimeoutException:
        return "AI响应超时，请稍后重试。"
    except httpx.HTTPStatusError as e:
        return f"AI服务异常（状态码：{e.response.status_code}），请检查API配置。"
    except Exception as e:
        return f"AI调用失败：{str(e)}"
