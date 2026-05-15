### Methodology: Undercover Game Engine (谁是卧底)

This document explains how the game works end to end, including phases, AI behavior, deception analysis, bidding, voting, and logging.

#### Core Data Model

- `GameState` (see `game_graph.py`): single source of truth containing:
  - Players, roles, alive lists, special role (Undercover)
  - Word pair: `civilian_word` and `undercover_word`
  - Turn/round counters: `round_num`, `step`, and `phase`
  - Action logs and summaries: bids, descriptions, votes, summaries
  - Deception tracking: `deception_history` and `deception_scores`
  - `game_logs`: append-only list of structured events (also streamed to disk)

#### Phases per Round

1) Describe
- Players bid for speaking priority
- The winner describes their word (without saying it directly)
- Deception analysis runs on every description
- Continues until all players have described

2) Vote
- Every player casts a vote for who they believe is the Undercover
- Votes are informed by deception scores accumulated throughout the game

3) Exile
- Majority vote determines who is eliminated
- The eliminated player's role is revealed

4) Check Winner
- Undercover eliminated → Civilians win
- Undercover survives until only 2 players remain → Undercover wins
- Otherwise → new round begins

5) Summarize
- All surviving players reflect on the game
- Full deception statistics are computed

6) End
- Final results printed with detailed deception analysis

Each phase is a node in a LangGraph `StateGraph`. Transitions are deterministic based on game rules and the evolving `GameState`.

#### AI Players (`player.py`)

- Each player is a `Player` with `role` (Civilian or Undercover), `word`, `scratchpad`, and a shared `llm`.
- Action methods: `describe` constructs a role-aware JSON prompt and calls `call_model`.
- `call_model` returns parsed JSON and also includes the exact `_prompt` and `_raw_response` for auditability.
- The Undercover is told their word is different from others and must blend in strategically.
- Civilians are told they share a word with other Civilians and must identify the Undercover.

#### Deception Detection (`deception_detection.py`)

- `DeceptionDetector` asks the active speaker to self-assess deception and asks all peers to analyze the description.
- Peer analyses run concurrently via a thread pool.
- Results are normalized and stored in `deception_history` and aggregated into `deception_scores` via weighted exponential smoothing (70% new, 30% historical).
- A per-round deception summary is produced at the end of the game.

#### Bidding and Description (`Bidding.py` and `game_graph.py`)

- Players bid for speaking order using `get_bid` (integer 0-10).
- `choose_next_speaker` resolves the next speaker — highest bid wins, with mention bias and random tiebreaking.
- `description_log` preserves all descriptions as `[speaker, text]` pairs.

#### Voting and Resolution

- `vote` collects each alive player's vote based on their perception of others' deceptiveness.
- `exile` removes the majority-voted player from `alive_players`.
- Win conditions:
  - Undercover eliminated → Civilians win
  - Undercover survives to ≤2 players → Undercover wins

#### Logging (`logs.py`)

- Every state transition or action appends a structured event via `log_event`.
- Events are streamed to `logs/<run_id>/events.ndjson` with concurrency safety.
- A final full `game_state.json` snapshot is written upon completion.
- Metadata for each run is written to `run_meta.json` and indexed in `logs/index.jsonl`.

#### Reproducibility and Auditing

- Prompts and raw model outputs are preserved in event details (`_prompt`, `_raw_response`).
- Fallbacks are explicitly logged (e.g., when a model returns an invalid output).
- Deception analyses retain chain-of-thought fields in raw form for offline study.

#### Extending the System

- Add new phases by extending `GameState.phase` literals and adding nodes to `StateGraph`.
- Use `log_event` for any new actions; include both `inputs` and `outputs` fields.
- Register additional per-run artifacts by updating `init_logging_state` in `logs.py`.
