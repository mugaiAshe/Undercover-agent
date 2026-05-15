from game_graph import graph, GameState, WORD_PAIRS
from player import Player
from langchain_openai import ChatOpenAI
import os, random, argparse
from dotenv import load_dotenv
from logs import init_logging_state, write_final_state, print_header, print_subheader, print_kv, write_final_metrics

load_dotenv()

os.environ["OPENAI_API_KEY"] = "sk-"
api_key = os.getenv("OPENAI_API_KEY")


def get_llm(model_name="deepseek-v4-flash", api_key=None):
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    elif not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set")
    os.environ["MODEL_NAME"] = model_name
    return ChatOpenAI(
        model=model_name, temperature=0.7,
        base_url="https://api.deepseek.com",
        request_timeout=120, max_retries=3
    )


def run_game(model_name="deepseek-v4-flash", api_key=None,
             log_dir: str = "./logs", enable_file_logging: bool = True,
             word_pair: tuple = None):
    print_header("Starting Undercover Game (谁是卧底)")
    print_kv("Model", model_name)

    llm = get_llm(model_name, api_key)

    # Pick word pair
    if word_pair:
        civilian_word, undercover_word = word_pair
    else:
        civilian_word, undercover_word = random.choice(WORD_PAIRS)

    # Setup players: 4 players, 1 undercover
    players = ["Alice", "Bob", "Selena", "Raj"]
    undercover_name = random.choice(players)
    civilians = [p for p in players if p != undercover_name]

    print_kv("Civilian word", civilian_word)
    print_kv("Undercover word", undercover_word)
    print_kv("Undercover", undercover_name)

    roles = {}
    for name in players:
        roles[name] = "Undercover" if name == undercover_name else "Civilian"

    player_objects = {}
    for name in players:
        word = undercover_word if name == undercover_name else civilian_word
        player_objects[name] = Player(name=name, role=roles[name], word=word, llm=llm)

    initial_state = GameState(
        round_num=0,
        players=players,
        alive_players=players.copy(),
        roles=roles,
        undercover=undercover_name,
        civilians=civilians,
        civilian_word=civilian_word,
        undercover_word=undercover_word,
        phase="describe",
        game_logs=[],
        deception_history={},
        deception_scores={},
    )

    initial_state = init_logging_state(initial_state, log_dir=log_dir, enable_file_logging=enable_file_logging)

    print_subheader("Execute")
    print_kv("Action", "Compiling and running the game graph...")
    runnable = graph.compile()
    final_state = runnable.invoke(initial_state, config={
        "recursion_limit": 1000,
        "configurable": {
            "player_objects": player_objects,
        }
    })

    write_final_state(final_state)
    write_final_metrics(final_state)

    print_subheader("Status")
    print_kv("Result", "Game completed successfully!")

    paths = getattr(final_state, "log_paths", {})
    if paths:
        print_subheader("Log Files")
        print_kv("Events (NDJSON)", paths.get('events'), indent=2)
        print_kv("Final State JSON", paths.get('state'), indent=2)
        print_kv("Final Metrics JSON", paths.get('metrics'), indent=2)
        print_kv("Run Metadata", paths.get('meta'), indent=2)
    return final_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Undercover Game (谁是卧底) with AI players")
    parser.add_argument("--model", default="deepseek-v4-flash", help="Model name")
    parser.add_argument("--api-key", help="OpenAI-compatible API key")
    parser.add_argument("--log-dir", default="./logs", help="Log directory")
    parser.add_argument("--no-file-logging", action="store_true", help="Disable file logging")
    args = parser.parse_args()

    try:
        final_state = run_game(args.model, args.api_key,
                               log_dir=args.log_dir,
                               enable_file_logging=(not args.no_file_logging))

        print_subheader("Game Results")
        alive = final_state["alive_players"] if isinstance(final_state, dict) else final_state.alive_players
        print_kv("Final alive players", alive, indent=2)
        winner = final_state.get("winner") if isinstance(final_state, dict) else getattr(final_state, 'winner', None)
        if winner:
            print_kv("Winner", winner, indent=2)

    except Exception as e:
        print_subheader("Error")
        print_kv("Message", f"{e}")
        import traceback
        traceback.print_exc()
