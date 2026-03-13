"""金融分析智能体 - 主入口"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()

    print(f"🚀 金融分析智能体启动中...")
    print(f"📁 数据目录: {settings.project_dir}")

    yield

    print("🛑 正在关闭...")


app = FastAPI(
    title="金融分析智能体 API",
    description="个人本地私有化部署的金融分析工具",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "金融分析智能体 API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("src.main:app", host=settings.api_host, port=settings.api_port, reload=True)
