import random
# DeepSeek API uses OpenAI-compatible SDK
from langchain_openai import ChatOpenAI
import os

_llm = None


def get_llm():
    """Lazily initialize the DeepSeek LLM instance."""
    global _llm
    if _llm is None:
        model_name = os.environ.get("MODEL_NAME", "deepseek-v4-flash")
        _llm = ChatOpenAI(
            model=model_name, temperature=0.7,
            base_url="https://api.deepseek.com",
            request_timeout=120, max_retries=3
        )
    return _llm


def get_bid(player_name: str, dialogue_history: str):
    """
    Calls DeepSeek to get a bid (0-10) from a player based on descriptions so far.
    """
    prompt = f"""
You are a player in a game of "Who is the Undercover". Your name is {player_name}.
Here are the descriptions so far:

{dialogue_history}

How strongly do you want to describe your word next? Return a single number from 0 to 10.
0 = no desire to speak. 10 = extremely eager to speak.
Only respond with the number. Do not explain.
"""
    response = get_llm().invoke(prompt, timeout=60).content.strip()
    try:
        bid = int(response)
        bid = max(0, min(10, bid))
    except ValueError:
        bid = 0
    return bid, response


def get_max_bids(bid_dict):
    max_value = max(bid_dict.values())
    return [name for name, bid in bid_dict.items() if bid == max_value]


def choose_next_speaker(bid_dict, previous_dialogue=None):
    """
    Given a dictionary of player bids, returns the chosen speaker using:
    - Max bid
    - Mention bias from previous dialogue
    - Random tiebreaking
    """
    top_bidders = get_max_bids(bid_dict)
    if previous_dialogue:
        top_bidders += [name for name in top_bidders if name in previous_dialogue]
    random.shuffle(top_bidders)
    return random.choice(top_bidders)
