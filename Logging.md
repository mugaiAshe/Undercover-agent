### 日志记录与数据访问

本项目将每次运行的所有游戏事件流式写入磁盘，并在运行结束时写入一份完整的状态 JSON 快照。

- 事件日志 (NDJSON)：`logs/<run_id>/events.ndjson`
  - 每行一个 JSON 对象，按时间顺序排列
  - 包含：时间戳、轮次、步骤、阶段、事件类型、参与者以及 `details`（详细信息）
  - `details` 中可能包含 `_prompt` 和 `_raw_response` 下的原始模型提示词与响应
- 最终状态 JSON：`logs/<run_id>/game_state.json`
  - 完整的 Pydantic 序列化 `GameState`，包括 `game_logs`、欺骗历史记录、评分等
- 最终指标 JSON：`logs/<run_id>/final_metrics.json`
  - 仅包含干净的研究级指标（不含原始提示词/响应）
  - 包含：每位玩家的欺骗统计和平均可疑度、交叉感知评分矩阵、每位观察者的检测准确率（准确率/精确率/召回率/F1），以及平均可疑度和观察者标记欺骗比例的时间/轮次趋势
- 运行元数据：`logs/<run_id>/run_meta.json`
  - 玩家、角色、词语、模型名称、时间戳
- 运行索引：`logs/index.jsonl`
  - 一行 JSON，包含所有历史运行及其路径

#### 配置日志保存位置

- 命令行参数：`--log-dir ./logs`（默认为 `./logs`）
- 完全禁用文件日志：`--no-file-logging`
- 环境变量方式：`LOG_DIR=/自定义路径 python3 run.py`

#### jq 快速示例

- 在游戏运行时实时查看事件：
```bash
jq -c . logs/<run_id>/events.ndjson
```

- 仅筛选描述事件：
```bash
jq -c 'select(.event=="describe")' logs/<run_id>/events.ndjson
```

- 提取所有原始模型响应以供审计：
```bash
jq -r 'select(.details._raw_response) | .details._raw_response' logs/<run_id>/events.ndjson
```

- 从快照中获取最终胜者和存活者：
```bash
jq '.winner, .alive_players' logs/<run_id>/game_state.json
```

- 列出最近的运行记录：
```bash
tail -n 20 logs/index.jsonl | jq -c .
```

#### 记录的内容

- 描述动作：describe（包含模型提示词和原始响应）
- 投票动作：vote、exile
- 欺骗分析：每条描述的自我分析和同伴分析
- 阶段转换和胜负判定

所有原始模型响应和确切提示词均保存在 `_raw_response` 和 `_prompt` 下，以确保可复现性。
