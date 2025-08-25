import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api.v1.game_ws import ConnectionManager

class TestConnectionManager:
    """ConnectionManager类的单元测试"""
    
    @pytest.fixture
    def connection_manager(self):
        """创建ConnectionManager实例"""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """创建模拟的WebSocket实例"""
        websocket = AsyncMock()
        websocket.send_text = AsyncMock()
        return websocket
    
    def test_init(self, connection_manager):
        """测试初始化"""
        assert connection_manager.active_connections == {}
        assert connection_manager.client_to_player == {}
        assert connection_manager.player_to_client == {}
    
    @pytest.mark.asyncio
    async def test_connect(self, connection_manager, mock_websocket):
        """测试连接功能"""
        client_id = "test_client_1"
        
        await connection_manager.connect(mock_websocket, client_id)
        
        assert client_id in connection_manager.active_connections
        assert connection_manager.active_connections[client_id] == mock_websocket
        assert connection_manager.get_connection_count() == 1
    
    def test_disconnect(self, connection_manager):
        """测试断开连接功能"""
        client_id = "test_client_1"
        player_id = "player_1"
        
        # 先注册连接和玩家
        connection_manager.active_connections[client_id] = MagicMock()
        connection_manager.client_to_player[client_id] = player_id
        connection_manager.player_to_client[player_id] = client_id
        
        # 断开连接
        connection_manager.disconnect(client_id)
        
        assert client_id not in connection_manager.active_connections
        assert client_id not in connection_manager.client_to_player
        assert player_id not in connection_manager.player_to_client
        assert connection_manager.get_connection_count() == 0
    
    def test_register_player(self, connection_manager):
        """测试注册玩家功能"""
        client_id = "test_client_1"
        player_id = "player_1"
        
        connection_manager.register_player(client_id, player_id)
        
        assert connection_manager.client_to_player[client_id] == player_id
        assert connection_manager.player_to_client[player_id] == client_id
    
    def test_get_player_id(self, connection_manager):
        """测试根据客户端ID获取玩家ID"""
        client_id = "test_client_1"
        player_id = "player_1"
        
        connection_manager.client_to_player[client_id] = player_id
        
        result = connection_manager.get_player_id(client_id)
        assert result == player_id
        
        # 测试不存在的客户端ID
        result = connection_manager.get_player_id("non_existent")
        assert result is None
    
    def test_get_client_id(self, connection_manager):
        """测试根据玩家ID获取客户端ID"""
        client_id = "test_client_1"
        player_id = "player_1"
        
        connection_manager.player_to_client[player_id] = client_id
        
        result = connection_manager.get_client_id(player_id)
        assert result == client_id
        
        # 测试不存在的玩家ID
        result = connection_manager.get_client_id("non_existent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager, mock_websocket):
        """测试发送个人消息"""
        client_id = "test_client_1"
        message = {"type": "test", "content": "hello"}
        
        # 先建立连接
        await connection_manager.connect(mock_websocket, client_id)
        
        # 发送消息
        await connection_manager.send_personal_message(message, client_id)
        
        # 验证消息被发送
        mock_websocket.send_text.assert_called_once()
        call_args = mock_websocket.send_text.call_args[0][0]
        assert "hello" in call_args
    
    def test_get_connected_players(self, connection_manager):
        """测试获取已连接玩家列表"""
        # 注册几个玩家
        connection_manager.register_player("client_1", "player_1")
        connection_manager.register_player("client_2", "player_2")
        
        players = connection_manager.get_connected_players()
        assert len(players) == 2
        assert "player_1" in players
        assert "player_2" in players
    
    def test_get_connection_count(self, connection_manager):
        """测试获取连接数"""
        assert connection_manager.get_connection_count() == 0
        
        # 添加连接
        connection_manager.active_connections["client_1"] = MagicMock()
        connection_manager.active_connections["client_2"] = MagicMock()
        
        assert connection_manager.get_connection_count() == 2
    
    def test_is_connected(self, connection_manager):
        """测试检查客户端是否已连接"""
        client_id = "test_client_1"
        
        assert connection_manager.is_connected(client_id) == False
        
        connection_manager.active_connections[client_id] = MagicMock()
        assert connection_manager.is_connected(client_id) == True
    
    def test_is_player_connected(self, connection_manager):
        """测试检查玩家是否已连接"""
        player_id = "player_1"
        
        assert connection_manager.is_player_connected(player_id) == False
        
        connection_manager.player_to_client[player_id] = "client_1"
        assert connection_manager.is_player_connected(player_id) == True

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
