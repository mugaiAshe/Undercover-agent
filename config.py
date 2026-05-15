# Undercover Game (谁是卧底) Configuration

# Available DeepSeek models
AVAILABLE_MODELS = {
    "deepseek-v4-flash": {
        "name": "deepseek-v4-flash",
        "description": "DeepSeek V4 Flash — fast and efficient",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "deepseek"
    },
    "deepseek-v4-pro": {
        "name": "deepseek-v4-pro",
        "description": "DeepSeek V4 Pro — flagship reasoning model with 1M context",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "deepseek"
    },
    "deepseek-chat": {
        "name": "deepseek-chat",
        "description": "DeepSeek Chat — general-purpose chat model",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "deepseek"
    },
}

DEFAULT_MODEL = "deepseek-v4-flash"

# Game settings
GAME_CONFIG = {
    "player_names": ["Alice", "Bob", "Selena", "Raj"],
}

# Environment settings
ENV_CONFIG = {
    "deepseek_api_key_env": "DEEPSEEK_API_KEY",
    "debug_mode": True,
    "log_level": "INFO"
}
