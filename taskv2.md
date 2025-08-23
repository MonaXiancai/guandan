# AI 掼蛋大师 (Guandan Masters with AI) - MVP 详细构建计划 (V2)

### **MVP 目标 (已更新)**
创建一个功能更完整的单局游戏。实现2v2组队、计分升级、进贡/抗贡、级牌和红桃逢人配规则。1名人类玩家和3名AI玩家。游戏能完成一个完整的“打-升级-进贡-再打”的闭环。

---

### **阶段 0 & 1 (部分已完成)**
* **任务 0.1 - 0.3:** (已完成) 项目初始化与环境设置
* **任务 1.1 - 1.2:** (已完成) 创建 `Card` 和 `Deck` 类
* **任务 1.3 - 1.4:** (已完成) 创建牌型解析和比较的 **初版** 逻辑
* **任务 1.5:** (已完成) 创建 `Player` 和 `GameState` 基础类

---

### **阶段 1.5: 核心逻辑重构与扩展 (新任务从此开始)**

**目标:** 将新的复杂规则集成到核心逻辑中，为完整的游戏循环做准备。

* **任务 1.6: 扩展 `GameState` 和 `Player`**
    * **文件:** `game_state.py`, `player.py`
    * **操作:**
        1.  在 `GameState` 中添加新属性: `current_level: int`, `declarer_team: int` (当前打级的队伍，0或1), `last_round_finish_order: list[str]` (用于判断名次和进贡)。
        2.  在 `Player` 中添加新属性: `team: int` (所属队伍，0或1)。
    * **验收标准:** 新属性可以被成功设置和读取。

* **任务 1.7: 重构 `Card` 类的辅助功能**
    * **文件:** `card.py`
    * **操作:**
        1.  移除 `Card` 类中的 `__lt__` 排序方法，以避免混淆。
        2.  添加辅助方法 `is_joker() -> bool`, `is_big_joker() -> bool`。
        3.  添加辅助方法 `is_trump(level: int) -> bool`，判断该牌是否是级牌。
        4.  添加辅助方法 `is_wildcard(level: int) -> bool`，判断该牌是否是红桃级牌。
    * **验收标准:** `Card(Rank.SEVEN, Suit.HEART).is_wildcard(7)` 应返回 `True`。

* **任务 1.8: 重构牌型解析器以支持“逢人配”**
    * **文件:** `hand_validator.py`
    * **操作:**
        1.  修改函数签名: `parse_hand(cards: list[Card])` -> `parse_hand(cards: list[Card], level: int)`。
        2.  重写函数内部逻辑，使其能够识别红桃级牌作为“万能牌”，并正确解析出包含万能牌的顺子、同花顺、三带二等组合。这是一个复杂任务，需要大量测试。
    * **验收标准:** `parse_hand([H7, S8, S9, S10, SJ], 7)` (H7是红桃7) 应能被正确解析为顺子。

* **任务 1.9: 重构牌型比较器以支持“级牌最大”**
    * **文件:** `hand_validator.py`
    * **操作:**
        1.  修改函数签名: `is_valid_play(new_hand, last_hand)` -> `is_valid_play(new_hand, last_hand, level: int)`。
        2.  重写比较逻辑，正确处理级牌炸弹 > 普通炸弹 > 其他牌型，以及单张级牌大于普通牌的规则。
    * **验收标准:** `is_valid_play([S7, C7, D7, H7], [S10, C10, D10, H10], 7)` 应返回 `True`。

* **任务 1.10: 实现进贡/抗贡逻辑**
    * **文件:** `game_engine.py`
    * **操作:** 创建一个纯逻辑函数 `calculate_tribute()`。它根据 `last_round_finish_order` 来决定谁该进贡、谁接收、进贡几张。再创建一个函数 `handle_tribute(tribute_info, players)`，它会检查玩家手牌（是否有双大王），执行实际的卡牌交换，并记录是否发生抗贡。
    * **验收标准:** 单元测试。给定不同的结束名次和手牌，函数能正确返回进贡方案和交换后的手牌。

* **任务 1.11: 实现完整的 `GameEngine` 状态机**
    * **文件:** `game_engine.py`
    * **操作:** 重构 `GameEngine`。将游戏流程划分为明确的状态：`PRE_GAME`, `TRIBUTING`, `PLAYING`, `ROUND_OVER`。
        1.  扩展 `start_new_game`，使其在发牌后进入 `TRIBUTING` 状态并调用进贡逻辑。
        2.  在进贡结束后，根据进贡/抗贡结果确定先手玩家，并切换到 `PLAYING` 状态。
        3.  扩展 `process_player_action`，增加玩家出完手牌后的逻辑，记录名次。
        4.  当所有玩家出完牌，切换到 `ROUND_OVER` 状态，计算得分，更新下一局的 `current_level`。
    * **验收标准:** `GameEngine` 可以通过一系列方法调用，完整地模拟一局从发牌、进贡、出牌到结束计分的流程。

---

### **阶段 2: 后端 - API层与网络 (进度: 0% 从此开始)**

**目标:** 将功能完备的游戏引擎通过 WebSocket 暴露给外部世界，使其能够被客户端连接和交互。

* **任务 2.1: 创建基础 FastAPI 服务器**
    * **文件:** `backend/app/main.py`
    * **操作:** 编写一个最简单的 FastAPI 应用，包含一个根路由 `@app.get("/")` 返回 `{"status": "ok"}`。配置 Uvicorn 启动脚本。
    * **验收标准:** 在 `backend` 目录运行 `uvicorn app.main:app --reload`，访问 `http://127.0.0.1:8000` 能看到 `{"status": "ok"}`。

* **任务 2.2: 实现 WebSocket 连接管理器**
    * **文件:** `backend/app/api/v1/game_ws.py`
    * **操作:** 创建一个 `ConnectionManager` 类，用于集中管理（添加、移除、广播）所有活跃的 WebSocket 连接。这是实现多人同步的基础。
    * **验收标准:** 该类的方法可以被单元测试验证其添加、移除和广播的逻辑正确性。

* **任务 2.3: 实现 WebSocket 端点并处理连接**
    * **文件:** `backend/app/main.py`, `backend/app/api/v1/game_ws.py`
    * **操作:** 在 `main.py` 中实例化一个全局的 `GameEngine`。在 `game_ws.py` 中创建 WebSocket 端点 `@router.websocket("/ws/{client_id}")`。当有新客户端连接时，使用 `ConnectionManager` 接受并存储该连接。
    * **验收标准:** 可以使用 WebSocket 客户端工具连接到该端点，服务器不会报错，并且连接被管理器记录。

* **任务 2.4: 触发游戏开始与首次状态广播**
    * **文件:** `backend/app/api/v1/game_ws.py`
    * **操作:** 修改 WebSocket 连接逻辑：当第四个玩家成功连接时，自动调用全局 `game_engine.start_new_game()`。然后，编写一个 `broadcast_state()` 函数，它会从 `game_engine` 获取当前状态，为每个玩家生成一个定制化（隐藏他人手牌）的JSON，并通过 `ConnectionManager` 广播给所有客户端。
    * **验收标准:** 四个客户端连接后，每个客户端都会收到一次初始的游戏状态广播，包含各自的手牌和游戏阶段（应为 `TRIBUTING`）。

* **任务 2.5: 处理客户端的玩家动作事件**
    * **文件:** `backend/app/api/v1/game_ws.py`
    * **操作:** 在 WebSocket 的消息监听循环中，解析来自客户端的JSON消息。实现对 `{"event": "PLAY_CARDS", ...}` 和 `{"event": "PASS_TURN", ...}` 事件的处理。接收到事件后，调用 `game_engine` 中对应的处理方法，然后立即调用 `broadcast_state()` 广播更新后的游戏状态。
    * **验收标准:** 通过客户端工具发送合法的出牌事件，服务器能正确更新游戏状态并广播给所有连接者。

* **任务 2.6: 处理客户端的进贡动作事件**
    * **文件:** `backend/app/api/v1/game_ws.py`
    * **操作:** 在消息监听循环中，增加对 `{"event": "SUBMIT_TRIBUTE", ...}` 事件的处理。该事件只在游戏阶段为 `TRIBUTING` 时有效。接收到后，调用 `game_engine` 的进贡处理方法，然后广播状态。
    * **验收标准:** 在进贡阶段，发送正确的进贡事件能使游戏状态成功过渡到 `PLAYING` 阶段。

---

### **阶段 3: 前端 - UI 界面与交互 (进度: 0%)**

**目标:** 创建一个功能完善的前端应用，能够连接到后端，实时渲染复杂的游戏状态，并提供完整的用户交互。

* **任务 3.1: 创建基础 UI 组件 (`Card`, `Hand`, `Board`)**
    * **文件:** `frontend/src/components/`
    * **操作:** 创建纯展示性的 React 组件：`Card.jsx` (显示单张牌), `Hand.jsx` (渲染一手牌), `Board.jsx` (组合成四人牌桌布局)。
    * **验收标准:** 在 `App.jsx` 中使用假数据，可以渲染出一个静态的牌桌界面。

* **任务 3.2: 实现 WebSocket 服务与全局状态存储**
    * **文件:** `frontend/src/services/websocketService.js`, `frontend/src/store/gameStore.js`
    * **操作:** 使用 Zustand 或 Redux 创建 `gameStore`，需包含 `current_level`, `game_phase`, `players`, `my_hand` 等所有状态。编写 `websocketService` 用于连接后端，并在收到 `GAME_STATE_UPDATE` 消息时更新 `gameStore`。
    * **验收标准:** 服务能连接后端，并且 `gameStore` 的状态能被来自服务器的消息正确更新。

* **任务 3.3: 连接后端并渲染动态游戏状态**
    * **文件:** `frontend/src/App.jsx` 及各组件
    * **操作:** 在 `App.jsx` 中调用 `websocketService.connect()`。让所有UI组件从 `gameStore` 读取数据来渲染。根据 `current_level` 和 `my_hand` 高亮级牌和红桃逢人配。根据 `game_phase` 显示不同的全局提示（如“等待玩家进贡”）。
    * **验收标准:** 刷新页面，能自动连接并显示后端分发的初始手牌和游戏信息。

* **任务 3.4: 实现卡牌选择与动作提交**
    * **文件:** `frontend/src/components/Hand.jsx`, `frontend/src/components/Actions.jsx`
    * **操作:** 在 `Hand` 组件中实现卡牌的点击选择逻辑。创建 `Actions` 组件，包含【出牌】和【过牌】按钮。点击按钮时，通过 `websocketService` 向后端发送 `PLAY_CARDS` 或 `PASS_TURN` 事件。
    * **验收标准:** 用户可以在手牌区选择卡牌，并成功点击按钮向后端提交操作，同时所有客户端的界面会同步更新。

* **任务 3.5: 实现进贡交互界面**
    * **文件:** `frontend/src/components/TributeModal.jsx`
    * **操作:** 创建一个模态框组件。该组件根据 `gameStore` 的状态进行判断：当 `game_phase` 为 `TRIBUTING` 且当前用户是进贡方时，自动弹出。它允许用户选择手牌并点击【确定进贡】按钮，该按钮会发送 `SUBMIT_TRIBUTE` 事件。
    * **验收标准:** 游戏开始时，需要进贡的玩家会看到操作弹窗，而其他玩家看到等待提示。进贡成功后，弹窗消失，游戏进入出牌阶段。

---

### **阶段 4 & 5: 完整流程与 AI 集成 (进度: 0%)**

**目标:** 打通人类玩家与AI玩家的游戏循环，并最终集成强大的LLM AI。

* **任务 4.1: 端到端的人类玩家流程测试**
    * **操作:** 启动前后端，手动操作人类玩家，与（尚未实现的）AI占位逻辑进行一整局游戏。确保从连接、进贡、出牌、到一局结束的整个流程对人类玩家是通畅的。
    * **验收标准:** 人类玩家可以完整地玩一局游戏直到结束。

* **任务 5.1: 创建能理解新规则的“规则机器人”AI**
    * **文件:** `backend/app/ai/robot_agent.py`
    * **操作:** 创建一个 `RobotAgent` 类，其 `decide_move` 方法需接收完整的 `game_state` 对象。AI需要能够根据 `current_level` 判断级牌的价值，并懂得在适当的时候使用“红桃逢人配”来组成牌型。
    * **验收标准:** 单元测试。给定复杂的游戏状态，机器人能做出合法的、有基本策略的决策。

* **任务 5.2: 在游戏引擎中集成机器人**
    * **文件:** `backend/app/game_logic/game_engine.py`
    * **操作:** 修改 `GameEngine` 的主循环。当轮到AI玩家时，不再等待网络消息，而是直接调用 `RobotAgent.decide_move()`，获取决策并处理。然后继续这个循环，直到轮到人类玩家。
    * **验收标准:** 人类玩家出牌后，后端会自动、快速地模拟完所有AI玩家的回合，直到再次轮到人类玩家，然后将最终状态广播出来。

* **任务 5.3: (最终任务) 用能理解新规则的 LLM 替换机器人**
    * **文件:** `backend/app/ai/llm_agent.py`, `backend/app/ai/prompts.py`
    * **操作:** 更新 Prompt，必须清晰、结构化地向 LLM 解释所有游戏规则：2v2队伍、当前级别、级牌、红桃逢人配、进贡规则、场上局势等。在 `GameEngine` 中，将对 `RobotAgent` 的调用替换为对 `LLMAgent` 的API调用。
    * **验收标准:** 游戏可以由 1 个真实玩家和 3 个 LLM 驱动的 AI 完整地玩下来，且AI表现出一定的策略性。