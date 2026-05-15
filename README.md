# Undercover Game (谁是卧底)

## Game Overview

This is a multiplayer social deduction game where:
- **Civilians** (平民) share the same word and try to identify the one player with a different word
- **Undercover** (卧底) has a different but similar word and tries to blend in without being discovered

Each round, players describe their word without saying it directly. The Undercover must craft deliberately vague descriptions to survive, while Civilians try to give specific-enough descriptions to signal their shared knowledge. After all descriptions, everyone votes to eliminate the most suspicious player.

The game includes a sophisticated deception detection system that analyzes every description in real time to determine trustworthiness.

## Quick Start

See also: `LOGGING.md` and `METHODOLOGY.md` for detailed logging and methodology docs.

### Prerequisites
- Python 3.8+
- OpenAI-compatible API key (DeepSeek, OpenAI, etc.)

### Installation

1. **Clone and setup the environment:**
```bash
git clone <repository-url>
cd undercover-game
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up your API key:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. **Run the game:**
```bash
python3 run.py
```

### Game Features

- **Dynamic AI Players**: Each player has their own personality and strategy
- **Advanced Deception Detection**: Real-time analysis of player descriptions for deceptive intent
- **Bidding-Based Speaking Order**: Players bid for the chance to describe their word, creating dynamic turn-taking
- **Voting System**: Democratic elimination voting with deception analysis
- **Game State Tracking**: Comprehensive logging of all game events

## Project Structure

```
undercover-game/
├── run.py                  # Main game entry point
├── game_graph.py           # Game logic and state machine
├── player.py               # Player class with AI behavior
├── deception_detection.py  # Deception analysis system
├── Bidding.py              # Bidding mechanics for speaking order
├── config.py               # Game configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## How to Play

### Game Flow

1. **Setup Phase**:
   - A word pair is selected (e.g. "苹果" vs "梨")
   - One player is randomly chosen as the Undercover and receives the different word
   - All other players (Civilians) receive the same word

2. **Description Phase**:
   - Players bid for speaking priority
   - Each player describes their word without saying it directly
   - Deception detection analyzes every description in real time

3. **Voting Phase**:
   - All players vote for who they think is the Undercover
   - Majority vote eliminates a player

4. **Win Condition Check**:
   - If the Undercover is eliminated → Civilians win
   - If the Undercover survives until only 2 players remain → Undercover wins
   - Otherwise → new round begins

### Player Roles

- **Civilian** (平民): Shares the same word with other Civilians. Tries to give specific-enough descriptions to signal shared knowledge while identifying vague or off descriptions from the Undercover.
- **Undercover** (卧底): Has a different word from everyone else. Must be deliberately vague to blend in, while trying to guess what the Civilians' word might be.

## Deception Detection

The game includes a sophisticated deception detection system that:

- **Self-Analysis**: Players analyze their own descriptions for deceptive intent
- **Peer Analysis**: Other players analyze each description for deception
- **Historical Tracking**: Maintains deception history for each player
- **Confidence Scoring**: Provides confidence levels for deception assessments
- **Chain-of-Thought Reasoning**: Step-by-step reasoning for every deception judgment

## Configuration

Edit `config.py` to customize:
- Number of players
- Model selection
- Game parameters
- Debug settings

## Game Logs

The game generates comprehensive logs. See `LOGGING.md` for full details.
- Events (NDJSON): One JSON event per line streamed during the run
- Final State JSON: Complete final game state
- Console output: Real-time game events
- Deception analysis: Detailed deception assessments

## Acknowledgments

- Built with LangChain and LangGraph
- Powered by DeepSeek / OpenAI-compatible LLM APIs
- Inspired by the classic "Who is the Undercover" (谁是卧底) party game
