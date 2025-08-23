# AI 掼蛋大师 (Guandan Masters with AI) - 架构设计文档

## 1. 总体架构理念

本项目采用现代 Web 开发中经典的 **前后端分离** 架构。

- **后端 (Backend):** 作为无头 (Headless) 服务，是整个系统的“大脑”。它负责处理所有游戏核心逻辑、管理游戏状态、验证规则，并与 AI 大模型进行通信。它不关心界面如何展示。
- **前端 (Frontend):** 作为纯客户端应用，是系统的“脸面”。它负责渲染游戏界面、接收用户的操作，并通过网络协议与后端进行实时通信，以更新和展示游戏状态。
- **AI 服务 (AI Services):** 作为外部依赖，是 AI 玩家的“决策核心”。后端在需要时向这些服务发起请求，获取 AI 的决策。

这种架构的优势在于高度解耦、职责清晰，便于独立开发、测试和部署。

---

## 2. 文件与文件夹结构

推荐使用 Monorepo（单一代码库）结构，将前后端代码放在同一个 Git 仓库中，便于管理。

```plaintext
/ai-guandan-master/
|
├── backend/                  -- 后端 Python (FastAPI) 项目
|   ├── app/                  -- 应用程序核心代码
|   |   ├── api/              -- API 路由/端点定义
|   |   |   └── v1/
|   |   |       └── game_ws.py  -- WebSocket 游戏通信路由
|   |   |
|   |   ├── core/             -- 配置, 全局设置, 启动事件
|   |   |   └── config.py     -- 环境变量和配置管理
|   |   |
|   |   ├── game_logic/       -- **核心游戏逻辑 (与Web框架无关)**
|   |   |   ├── card.py       -- 定义 Card, Suit, Rank 类
|   |   |   ├── deck.py       -- 定义 Deck 类 (发牌, 洗牌)
|   |   |   ├── hand_validator.py -- 【关键】牌型和出牌合法性验证器
|   |   |   ├── game_state.py -- 定义 GameState 类 (管理一局游戏的状态)
|   |   |   ├── player.py     -- 定义 Player, HumanPlayer, AIPlayer 类
|   |   |   └── game_engine.py  -- 游戏主引擎, 驱动游戏流程
|   |   |
|   |   ├── ai/               -- AI 对接相关模块
|   |   |   ├── llm_agent.py  -- 封装与大模型 API 的交互
|   |   |   └── prompts.py    -- 存储和管理 Prompt 模板
|   |   |
|   |   └── main.py           -- FastAPI 应用入口
|   |
|   ├── tests/                -- 单元测试和集成测试
|   |   └── test_game_logic.py -- 针对 hand_validator.py 的重点测试
|   |
|   ├── .env                  -- 环境变量 (API Keys 等)
|   ├── Dockerfile            -- Docker 镜像配置文件
|   └── requirements.txt      -- Python 依赖
|
├── frontend/                 -- 前端 React / Vue 项目
|   ├── public/               -- 静态资源 (index.html, favicons)
|   ├── src/                  -- 前端源代码
|   |   ├── assets/           -- 图片 (牌面), 声音等资源
|   |   ├── components/       -- 可复用的 UI 组件
|   |   |   ├── Board.jsx     -- 游戏主面板
|   |   |   ├── Hand.jsx      -- 玩家手牌区域
|   |   |   ├── Card.jsx      -- 单张卡牌组件
|   |   |   ├── PlayerAvatar.jsx-- 玩家头像及信息组件
|   |   |   └── Actions.jsx   -- 操作按钮 (出牌, 过)
|   |   |
|   |   ├── services/         -- 外部通信服务
|   |   |   └── websocketService.js -- 封装 WebSocket 连接和事件处理
|   |   |
|   |   ├── store/            -- 全局状态管理 (Zustand/Redux)
|   |   |   └── gameStore.js  -- 存储从后端同步的游戏状态
|   |   |
|   |   ├── App.jsx           -- 应用主组件
|   |   └── main.jsx          -- 应用入口
|   |
|   ├── Dockerfile            -- 用于构建前端静态资源的 Docker 镜像
|   └── package.json          -- 项目依赖和脚本
|
├── docs/                     -- 项目文档
|   └── api.md                -- WebSocket 事件和 API 接口定义
|
├── docker-compose.yml        -- Docker Compose 编排文件 (一键启动前后端)
└── README.md                 -- 项目说明文件
```

---

## 3. 各模块核心作用

### Backend
- **`app/api/`**: 负责处理网络请求。`game_ws.py` 定义了 WebSocket 的连接、消息接收和广播逻辑。它是前端与后端游戏逻辑的桥梁。
- **`app/game_logic/`**: **项目的灵魂**。这里包含了所有纯粹的掼蛋游戏规则，它不依赖于任何网络框架。这种设计使得游戏逻辑可以被轻松地进行单元测试，甚至可以被移植到其他应用（如命令行工具）中。
  - `hand_validator.py` 尤为重要，它保证了任何出牌（无论来自人类还是 AI）的绝对合规性。
- **`app/ai/`**: 负责将游戏状态“翻译”成自然语言（Prompt），并调用外部 LLM API，再将返回的决策“翻译”回游戏指令。它是游戏逻辑与 AI 大脑之间的适配器。
- **`main.py`**: 启动 Web 服务器，并将所有路由和中间件组织起来。

### Frontend
- **`src/components/`**: 将 UI 拆分为多个独立的、可复用的组件，使代码更易于管理和维护。
- **`src/services/websocketService.js`**: 集中处理所有与后端的 WebSocket 通信。它会监听来自服务器的事件（如状态更新），并调用状态管理工具来更新 UI。同时，它也负责将用户的操作（如出牌）发送给服务器。
- **`src/store/gameStore.js`**: **前端的状态中心**。它存储了从后端接收到的最新游戏状态，当状态变更时，UI 组件会自动重新渲染，确保用户看到的界面永远是同步的。

---

## 4. 状态存储位置 (State Management)

**核心原则：唯一可信源 (Single Source of Truth) 永远在后端。**

1.  **游戏主状态 (Authoritative State):**
    - **存储位置:** **后端服务器的内存中**。
    - **具体实现:** 在 `game_engine.py` 中，会有一个全局的字典或类来管理所有正在进行的游戏局。例如: `active_games = {"game_id_123": GameState_Object, ...}`。
    - **`GameState` 对象** 包含了关于一局游戏的所有信息：所有玩家的手牌、当前轮到谁、当前的牌级、桌面上最后一手牌等等。
    - **优点:** 速度极快，无需数据库读写延迟。
    - **缺点:** 如果后端服务重启，所有进行中的游戏都会丢失。对于此项目，这是可以接受的。若要实现断线重连，则需要将 `GameState` 对象序列化后存入 **Redis** 这样的内存数据库中。

2.  **前端状态 (UI State / Mirrored State):**
    - **存储位置:** **前端浏览器的内存中**，由状态管理库（如 Zustand, Redux）管理。
    - **作用:** 它是后端主状态的一个“镜像”或“缓存”。前端从不直接修改这个状态来影响游戏逻辑。它仅在接收到后端通过 WebSocket 推送的 `GAME_STATE_UPDATE` 事件时才更新自己。
    - **流程:** 用户点击【出牌】 -> 前端通过 WebSocket 发送 `PLAY_CARD` 事件给后端 -> 后端验证并更新主状态 -> 后端广播 `GAME_STATE_UPDATE` 给所有客户端 -> 前端接收事件并更新自己的 store，从而触发 UI 刷新。

---

## 5. 服务之间如何连接 (Service Communication)

服务间的连接清晰地定义了数据如何流动。

```mermaid
graph TD
    subgraph Browser
        Frontend[前端 UI (React/Vue)]
    end

    subgraph Server
        Backend[后端应用 (FastAPI)]
    end

    subgraph AI Cloud
        LLM_API[大模型 API (e.g., OpenAI, Gemini)]
    end

    %% Connections
    Frontend -- HTTP/HTTPS for initial page load --> Backend
    Frontend -- WebSocket (双向实时) --> Backend
    Backend -- HTTPS REST API (请求/响应) --> LLM_API

```

1.  **前端 ↔ 后端:**
    - **协议:** **WebSocket**
    - **流程:**
        - 前端通过 WebSocket URL (`ws://localhost:8000/api/v1/ws/{game_id}`) 连接到后端。
        - **客户端发送事件 (Client -> Server):** 用户操作被包装成 JSON 消息发送。
          ```json
          // 用户出牌
          { "event": "PLAY_CARDS", "payload": { "cards": ["H5", "S5", "D5"] } }
          // 用户过牌
          { "event": "PASS_TURN", "payload": {} }
          ```
        - **服务器广播事件 (Server -> Clients):** 每当游戏状态发生改变（如一个玩家出牌后），服务器会向该局游戏的所有客户端广播最新的完整游戏状态。
          ```json
          {
            "event": "GAME_STATE_UPDATE",
            "payload": {
              "currentPlayer": "player_2",
              "lastPlayedHand": { "type": "pair", "cards": ["H4", "S4"] },
              "players": [
                { "id": "player_1", "cardCount": 15 },
                { "id": "player_2", "cardCount": 20, "isHuman": false }
              ],
              "yourHand": ["S_JOKER", "H_ACE", "..."] // 'yourHand' 对每个玩家是定制的
            }
          }
          ```

2.  **后端 ↔ AI 大模型服务:**
    - **协议:** **HTTPS (REST API)**
    - **流程:**
        - 当轮到 AI 玩家出牌时，后端的 `AIAgent` 被触发。
        - `AIAgent` 从当前的 `GameState` 对象中提取所有必要信息。
        - `AIAgent` 构建一个包含角色、上下文和指令的 Prompt。
        - `AIAgent` 使用 `requests` 或 `httpx` 库向大模型的 API 端点（如 `api.openai.com/v1/chat/completions`）发送一个 **POST** 请求，请求体为包含 Prompt 的 JSON 数据。
        - 后端 **同步等待** API 的响应。
        - 收到响应后，解析返回的 JSON，提取出 `{"action": "play", ...}`，并交由 `game_engine` 处理。

这个架构设计兼顾了实时性、模块化和可扩展性，为你启动项目提供了一个坚实的基础。