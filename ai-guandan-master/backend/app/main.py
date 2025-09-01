from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
import uvicorn
from typing import Dict, List
import json

# 导入WebSocket相关功能
from app.api.v1.game_ws import websocket_endpoint, connection_manager
# 导入游戏引擎
from app.game_logic.game_engine import GameEngine

app = FastAPI(title="Guandan Masters API", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局游戏引擎实例
game_engine = GameEngine()

# 创建API路由器
api_router = APIRouter(prefix="/api/v1")

# WebSocket路由
@api_router.websocket("/ws/{client_id}")
async def websocket_route(websocket: WebSocket, client_id: str):
    """
    WebSocket连接端点
    
    Args:
        websocket: WebSocket连接实例
        client_id: 客户端唯一标识
    """
    await websocket_endpoint(websocket, client_id)

# 将API路由器添加到主应用
app.include_router(api_router)

@app.get("/")
async def root():
    """根路由，用于健康检查"""
    return {"status": "ok", "message": "Guandan Masters API service running"}

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "Guandan Masters"}

@app.get("/connections")
async def get_connections():
    """获取当前连接信息"""
    return {
        "connection_count": connection_manager.get_connection_count(),
        "connected_players": connection_manager.get_connected_players()
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, 
                ws_ping_interval=1800.0, ws_ping_timeout=1800.0)
