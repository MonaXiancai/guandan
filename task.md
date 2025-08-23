# AI 掼蛋大师 (Guandan Masters with AI) - MVP 详细构建计划

### **MVP 目标**
创建一个可以玩的单局游戏。1名人类玩家和3名“硬编码”规则的AI玩家（在最后一步替换为LLM）。游戏能完成发牌、人类出牌、AI响应、广播状态的完整循环。不包含升级、进贡、UI美化等复杂功能。

---

### **阶段 0: 项目初始化与环境设置**

**目标:** 准备好开发环境和项目骨架。

* **任务 0.1: 创建项目目录结构**
    * **操作:** 在终端执行以下命令，创建整个项目的文件和文件夹骨架。
        ```bash
        mkdir -p ai-guandan-master/backend/app/api/v1 ai-guandan-master/backend/app/core ai-guandan-master/backend/app/game_logic ai-guandan-master/backend/app/ai ai-guandan-master/backend/tests
        mkdir -p ai-guandan-master/frontend/src/assets ai-guandan-master/frontend/src/components ai-guandan-master/frontend/src/services ai-guandan-master/frontend/src/store
        touch ai-guandan-master/backend/app/__init__.py ai-guandan-master/backend/app/main.py ai-guandan-master/backend/requirements.txt
        touch ai-guandan-master/frontend/src/App.jsx ai-guandan-master/frontend/src/main.jsx
        touch ai-guandan-master/docker-compose.yml ai-guandan-master/README.md
        ```
    * **验收标准:** 所有指定的文件夹和空文件都已创建。

* **任务 0.2: 初始化后端环境**
    * **操作:** 进入 `backend` 目录，创建Python虚拟环境，并安装 FastAPI 和 Uvicorn。
        ```bash
        cd ai-guandan-master/backend
        python3 -m venv venv
        source venv/bin/activate
        pip install fastapi "uvicorn[standard]"
        pip freeze > requirements.txt
        ```
    * **验收标准:** `backend/venv` 目录存在，`requirements.txt` 文件包含 `fastapi` 和 `uvicorn`。

* **任务 0.3: 初始化前端环境**
    * **操作:** 进入 `frontend` 目录，使用 Vite 初始化一个 React 项目。
        ```bash
        cd ai-guandan-master/frontend
        npm create vite@latest . -- --template react
        npm install
        ```
    * **验收标准:** `frontend` 目录包含 `package.json`, `vite.config.js` 和 `node_modules` 文件夹。`npm run dev` 命令可以成功启动一个默认的React页面。

---

### **阶段 1: 后端 - 核心游戏逻辑 (纯Python)**

**目标:** 在不涉及任何网络通信的情况下，构建稳定可靠的游戏规则引擎。

* **任务 1.1: 创建 `Card` 类**
    * **文件:** `backend/app/game_logic/card.py`
    * **操作:** 定义 `Suit` 和 `Rank` 的枚举类型。创建一个 `Card` 类，它包含 `rank` 和 `suit` 属性。为方便调试，实现 `__str__` 和 `__repr__` 方法。为方便排序，实现 `__lt__` (小于) 比较方法。
    * **验收标准:** 可以实例化一个 `Card` 对象，例如 `card = Card(Rank.ACE, Suit.SPADE)`，并且可以打印它。卡牌列表可以被正确排序。

* **任务 1.2: 创建 `Deck` 类**
    * **文件:** `backend/app/game_logic/deck.py`
    * **操作:** 创建一个 `Deck` 类。在构造函数中，生成两副标准的扑克牌（108张 `Card` 对象）。实现 `shuffle()` 方法来打乱牌堆，实现 `deal()` 方法来向N个玩家发牌，返回一个包含N个列表的列表（每个列表代表一个玩家的手牌）。
    * **验收标准:** `Deck()` 创建后包含108张牌。调用 `shuffle()` 后顺序改变。调用 `deal(4)` 返回4个各有27张牌的列表。

* **任务 1.3: 定义牌型常量和解析器**
    * **文件:** `backend/app/game_logic/hand_validator.py`
    * **操作:** 定义牌型枚举或常量，如 `SINGLE`, `PAIR`, `TRIO`, `STRAIGHT`, `BOMB` 等。编写一个独立的函数 `parse_hand(cards: list[Card])`，它接收一个已排序的卡牌列表，返回其牌型和主值（例如，顺子的最高牌，炸弹的牌点）。如果牌型不合法，则抛出异常或返回 `INVALID`。
    * **验收标准:** 单元测试。`parse_hand([Card('5S'), Card('5H')])` 应返回 `PAIR`。`parse_hand([Card('5S'), Card('6H')])` 应返回 `INVALID`。

* **任务 1.4: 实现牌型比较逻辑**
    * **文件:** `backend/app/game_logic/hand_validator.py`
    * **操作:** 编写一个函数 `is_valid_play(new_hand: list[Card], last_hand: list[Card])`。该函数内部调用 `parse_hand`，然后根据掼蛋规则（炸弹大于普通牌，同牌型比大小等）判断 `new_hand` 是否能大过 `last_hand`。
    * **验收标准:** 单元测试。`is_valid_play` 对比一对'6'和一对'5'应返回 `True`。对比一个四王炸弹和任何其他牌型都应返回 `True`。

* **任务 1.5: 创建 `Player` 和 `GameState` 类**
    * **文件:** `backend/app/game_logic/player.py` 和 `backend/app/game_logic/game_state.py`
    * **操作:** 创建一个简单的 `Player` 类，包含 `player_id` 和 `hand` (卡牌列表)。创建一个 `GameState` 类，包含 `players` 列表、`current_turn_index`、`last_played_hand` 和 `last_player_id` 等属性。
    * **验收标准:** 可以成功实例化 `GameState`，并为其填充 `Player` 对象。

* **任务 1.6: 创建 `GameEngine` 核心方法**
    * **文件:** `backend/app/game_logic/game_engine.py`
    * **操作:** 创建 `GameEngine` 类。实现 `start_new_game(player_ids: list[str])` 方法，该方法会初始化一个 `GameState`，创建 `Deck`，洗牌并发牌给所有玩家。实现 `process_player_action(player_id: str, cards: list[Card])` 方法，它会使用 `hand_validator` 验证出牌，如果合法，则更新 `GameState`（移出玩家手牌，更新 `last_played_hand`，轮转到下一个玩家）。
    * **验收标准:** 调用 `start_new_game` 后，`game_engine.game_state` 被正确填充。调用 `process_player_action` 使用合法的牌，`game_state` 会被更新；使用非法的牌，`game_state` 保持不变并返回错误。

---

### **阶段 2: 后端 - API层与网络**

**目标:** 将纯逻辑的游戏引擎通过 WebSocket 暴露给外部世界。

* **任务 2.1: 创建基础 FastAPI 服务器**
    * **文件:** `backend/app/main.py`
    * **操作:** 编写一个最简单的 FastAPI 应用，包含一个根路由 `@app.get("/")` 返回 `{"status": "ok"}`。
    * **验收标准:** 在 `backend` 目录运行 `uvicorn app.main:app --reload`，访问 `http://127.0.0.1:8000` 能看到 `{"status": "ok"}`。

* **任务 2.2: 实现 WebSocket 端点**
    * **文件:** `backend/app/api/v1/game_ws.py` 并在 `main.py` 中引入。
    * **操作:** 创建一个 WebSocket 端点 `@router.websocket("/ws/{client_id}")`。实现一个 `ConnectionManager` 类来管理所有活跃的 WebSocket 连接。当有新客户端连接时，接受连接并将其存入管理器。
    * **验收标准:** 可以使用一个简单的 WebSocket 客户端工具连接到该端点，服务器不会报错。

* **任务 2.3: 启动游戏与状态广播**
    * **文件:** `backend/app/main.py` (或一个游戏管理模块)
    * **操作:** 在后端全局实例化一个 `GameEngine`。修改 WebSocket 逻辑，当第四个玩家连接成功时，自动调用 `game_engine.start_new_game()`。然后，编写一个 `broadcast_state()` 函数，它会遍历所有连接，为每个玩家生成一个定制化的游戏状态（隐藏其他玩家的手牌），并将其发送出去。
    * **验收标准:** 四个客户端连接后，每个客户端都会收到一次初始的游戏状态广播。

---

### **阶段 3: 前端 - 基础展示与连接**

**目标:** 创建一个能连接到后端并展示游戏初始状态的静态页面。

* **任务 3.1: 创建静态 `Card` 和 `Hand` 组件**
    * **文件:** `frontend/src/components/Card.jsx`, `frontend/src/components/Hand.jsx`
    * **操作:** 创建一个 `Card` 组件，接收 `suit` 和 `rank` 作为 props 并显示一张牌。创建一个 `Hand` 组件，接收一个卡牌数组作为 props，并渲染一组 `Card` 组件。
    * **验收标准:** 在 `App.jsx` 中硬编码一些卡牌数据，`Hand` 组件能正确渲染出这手牌。

* **任务 3.2: 实现 WebSocket 服务与状态存储**
    * **文件:** `frontend/src/services/websocketService.js`, `frontend/src/store/gameStore.js`
    * **操作:** 使用 Zustand (或 React Context) 创建一个 `gameStore`，用于存放从后端接收的游戏状态。编写 `websocketService`，实现 `connect()` 方法和 `onMessage()` 监听器。当收到后端的 `GAME_STATE_UPDATE` 消息时，调用 `gameStore` 的 action 来更新状态。
    * **验收标准:** `connect()` 方法被调用后，`websocketService` 能与后端建立连接。

* **任务 3.3: 在主组件中连接并渲染**
    * **文件:** `frontend/src/App.jsx`
    * **操作:** 在 `App.jsx` 中，使用 `useEffect` 在组件加载时调用 `websocketService.connect()`。从 `gameStore` 中获取玩家手牌数据，并传递给 `Hand` 组件进行渲染。
    * **验收标准:** 刷新前端页面，它会自动连接到后端。如果后端已有4个连接，它会收到初始手牌数据并显示在屏幕上。

---

### **阶段 4: 实现人类玩家交互**

**目标:** 让用户可以通过点击界面来出牌或过牌。

* **任务 4.1: 实现前端卡牌选择逻辑**
    * **文件:** `frontend/src/components/Hand.jsx`
    * **操作:** 在 `Hand` 组件中添加状态来追踪被选择的卡牌。修改 `Card` 组件，为其添加 `onClick` 事件，点击时切换其选中状态。
    * **验收标准:** 在页面上点击手牌，被选中的牌有明显的视觉变化（如向上移动或边框高亮）。

* **任务 4.2: 添加操作按钮并发送事件**
    * **文件:** `frontend/src/components/Actions.jsx`
    * **操作:** 创建包含【出牌】和【过牌】按钮的 `Actions` 组件。点击【出牌】时，通过 `websocketService` 发送 `{"event": "PLAY_CARDS", "payload": ...}` 消息，内容为选中的卡牌。
    * **验收标准:** 点击按钮后，能在浏览器的开发者工具网络面板中看到 WebSocket 消息被正确发送出去。

* **任务 4.3: 后端处理人类玩家动作**
    * **文件:** `backend/app/api/v1/game_ws.py`
    * **操作:** 在 WebSocket 的消息接收逻辑中，解析收到的事件。如果是 `PLAY_CARDS`，则调用 `game_engine.process_player_action()`。无论操作成功与否，都调用 `broadcast_state()` 将最新的状态广播给所有玩家。
    * **验收标准:** 在前端点击出牌，如果合法，所有连接的客户端（在不同浏览器窗口中打开）都会看到桌面的牌和手牌数量发生变化。

---

### **阶段 5: 集成“机器人”AI玩家**

**目标:** 让AI能在轮到它们时自动出牌，完成MVP。

* **任务 5.1: 创建一个“规则机器人”AI**
    * **文件:** `backend/app/ai/robot_agent.py`
    * **操作:** 创建一个 `RobotAgent` 类，实现一个 `decide_move(hand, last_played_hand)` 方法。现在只实现最简单的逻辑：从自己的手牌中，找到能打过上一手牌的最小的一张单牌。如果找不到，就返回“过牌”。
    * **验收标准:** 单元测试。给定一手牌和`last_played_hand`，该方法能返回一个正确的出牌决策或“过牌”。

* **任务 5.2: 在游戏引擎中集成机器人**
    * **文件:** `backend/app/game_logic/game_engine.py`
    * **操作:** 修改 `GameEngine`。在轮转到下一个玩家时，检查该玩家是否是 AI。如果是，则**不要等待网络消息**，而是直接调用 `RobotAgent.decide_move()`，获取决策并处理。然后继续这个循环，直到轮到人类玩家或一轮结束。
    * **验收标准:** 人类玩家出牌后，后端会自动、快速地模拟完所有AI玩家的回合，直到再次轮到人类玩家，然后将最终状态广播出来。

* **任务 5.3: (MVP最终任务) 用 LLM 替换机器人**
    * **文件:** `backend/app/ai/llm_agent.py` 和 `backend/app/ai/prompts.py`
    * **操作:** 创建 `prompts.py` 并编写一个详细的 Prompt 模板。创建 `llm_agent.py`，实现对 OpenAI/Gemini API 的调用，将游戏状态和 Prompt 发送过去，并解析返回的 JSON。
    * **操作 2:** 在 `game_engine.py` 中，将调用的 `RobotAgent` 替换为新的 `LLMAgent`。
    * **验收标准:** 游戏可以完整地玩下来。当轮到AI时，后台会调用LLM API，AI会根据LLM的决策出牌。整个游戏循环流畅。