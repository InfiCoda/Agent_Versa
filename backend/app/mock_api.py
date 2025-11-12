#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地模拟API服务器
用于测试智能体评估系统，无需真实API

使用方法：
1. 启动模拟API: python mock_api.py
2. 在创建评估任务时，API端点填写: http://localhost:9000/api/chat
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI(title="智能体模拟API", description="用于测试的模拟智能体API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.7


class ChatResponse(BaseModel):
    response: str


# 预定义的模拟响应模板
RESPONSE_TEMPLATES = {
    "人工智能": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "Python": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。",
    "函数": "函数是一段可重复使用的代码，用于执行特定的任务。",
    "代码": "代码是用于编写程序的指令集合。",
    "机器学习": "机器学习是人工智能的一个子领域，使计算机能够从数据中学习。",
}


def generate_mock_response(prompt: str) -> str:
    """生成模拟响应"""
    prompt_lower = prompt.lower()
    
    # 根据关键词匹配预定义响应
    for keyword, response in RESPONSE_TEMPLATES.items():
        if keyword.lower() in prompt_lower:
            return response
    
    # 如果没有匹配，生成通用响应
    responses = [
        f"这是一个关于'{prompt[:30]}...'的问题。根据我的理解，这是一个有趣的话题。",
        f"关于'{prompt[:30]}...'，我可以提供以下信息：这是一个需要深入分析的领域。",
        f"针对您的问题'{prompt[:30]}...'，我的回答是：这是一个复杂的话题，需要多角度分析。",
    ]
    
    return random.choice(responses)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """模拟聊天接口"""
    response_text = generate_mock_response(request.prompt)
    
    return ChatResponse(response=response_text)


@app.get("/")
async def root():
    return {
        "message": "智能体模拟API服务",
        "endpoint": "/api/chat",
        "usage": "POST请求，body: {'prompt': '你的问题', 'max_tokens': 500, 'temperature': 0.7}"
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("启动模拟API服务器...")
    print("API端点: http://localhost:9000/api/chat")
    print("=" * 50)
    print("\n在评估任务中，使用以下配置：")
    print("  智能体API端点: http://localhost:9000/api/chat")
    print("  API密钥: 留空")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=9000)

