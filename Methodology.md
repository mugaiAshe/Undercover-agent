### 方法论文档：谁是卧底游戏引擎

本文档详细解释了游戏的端到端运作机制，包括各阶段、AI 行为、欺骗分析、竞价发言、投票系统和日志记录。

#### 核心数据模型

- `GameState`（参见 `game_graph.py`）：唯一的真实数据来源，包含：
  - 玩家、角色、存活列表、特殊角色（卧底）
  - 词语对：`civilian_word`（平民词）和 `undercover_word`（卧底词）
  - 回合/轮次计数器：`round_num`、`step` 和 `phase`
  - 动作日志和摘要：竞价、描述、投票、总结
  - 欺骗追踪：`deception_history` 和 `deception_scores`
  - `game_logs`：仅追加的结构化事件列表（同时流式写入磁盘）

#### 每轮各阶段

1) 描述阶段 (Describe)
- 玩家通过出价竞争发言优先级
- 获胜者在不直接说出词语的前提下描述自己的词
- 每次描述都会触发欺骗分析
- 持续进行直到所有玩家均已描述

2) 投票阶段 (Vote)
- 每位玩家根据自己认为谁是卧底进行投票
- 投票决策受游戏过程中累积的欺骗评分影响

3) 淘汰阶段 (Exile)
- 多数票决定谁被淘汰
- 被淘汰玩家的角色将被揭示

4) 胜负判定 (Check Winner)
- 卧底被淘汰 → 平民获胜
- 卧底存活至仅剩 2 人 → 卧底获胜
- 否则 → 开始新一轮

5) 总结阶段 (Summarize)
- 所有存活玩家对游戏进行反思
- 计算完整的欺骗统计数据

6) 结束阶段 (End)
- 打印最终结果和详细的欺骗分析报告

每个阶段都是 LangGraph `StateGraph` 中的一个节点。状态转换基于游戏规则和不断变化的 `GameState` 确定性执行。

#### AI 玩家 (`player.py`)

- 每位玩家都是一个 `Player` 对象，包含 `role`（Civilian 或 Undercover）、`word`（词语）、`scratchpad`（草稿本）和共享的 `llm`。
- 动作方法：`describe` 构建角色感知的 JSON 提示词并调用 `call_model`。
- `call_model` 返回解析后的 JSON，同时包含确切的 `_prompt` 和 `_raw_response` 以供审计。
- 卧底被告知其词语与他人不同，必须策略性地混入群体。
- 平民被告知他们与其他平民共享同一词语，必须识别出卧底。

#### 欺骗检测 (`deception_detection.py`)

- `DeceptionDetector` 要求当前发言者自我评估欺骗意图，并让所有同伴分析该描述。
- 同伴分析通过线程池并行执行。
- 结果经过规范化处理后存入 `deception_history`，并通过加权指数平滑（70% 新评估 + 30% 历史值）汇总到 `deception_scores` 中。
- 游戏结束时生成每轮的欺骗摘要。

#### 竞价与描述 (`Bidding.py` 和 `game_graph.py`)

- 玩家使用 `get_bid`（整数 0-10）竞标发言顺序。
- `choose_next_speaker` 决定下一发言人——最高出价者胜出，带有提及偏置和随机平局处理。
- `description_log` 将所有描述保存为 `[发言人, 文本]` 对。

#### 投票与结算

- `vote` 收集每位存活玩家的投票，基于其对他人欺骗程度的感知。
- `exile` 将获得多数票的玩家从 `alive_players` 中移除。
- 胜负条件：
  - 卧底被淘汰 → 平民获胜
  - 卧底存活至剩余人数 ≤ 2 → 卧底获胜

#### 日志记录 (`logs.py`)

- 每次状态转换或动作都通过 `log_event` 追加一条结构化事件。
- 事件以并发安全的方式流式写入 `logs/<run_id>/events.ndjson`。
- 运行完成时写入最终的完整 `game_state.json` 快照。
- 每次运行的元数据写入 `run_meta.json` 并索引到 `logs/index.jsonl`。

#### 可复现性与审计

- 提示词和原始模型输出保留在事件详情中（`_prompt`、`_raw_response`）。
- 回退策略被显式记录（例如模型返回无效输出时）。
- 欺骗分析以原始形式保留思维链字段，供离线研究使用。

#### 扩展系统

- 通过扩展 `GameState.phase` 字面量并向 `StateGraph` 添加新节点来新增阶段。
- 使用 `log_event` 记录任何新动作，包含 `inputs` 和 `outputs` 字段。
- 通过更新 `logs.py` 中的 `init_logging_state` 注册额外的运行产物。
