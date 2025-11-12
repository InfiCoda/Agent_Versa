"""FastAPI主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .models.database import init_db
from .api import tasks, indicators, results, system

# 创建FastAPI应用
app = FastAPI(
    title="智能体通用化特征评估工具",
    description="智能体通用化特征评估工具API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(tasks.router)
app.include_router(indicators.router)
app.include_router(results.router)
app.include_router(system.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 初始化数据库
    init_db()
    print("数据库初始化完成")


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能体通用化特征评估工具</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>智能体通用化特征评估工具 API</h1>
        <p>API文档: <a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
        <p>前端应用: <a href="http://localhost:8080">前端界面</a></p>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

