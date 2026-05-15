# Undercover Game (谁是卧底) Configuration

# Available models
AVAILABLE_MODELS = {
    "gpt-4o": {
        "name": "gpt-4o",
        "description": "OpenAI GPT-4o",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "openai"
    },
    "gpt-4o-mini": {
        "name": "gpt-4o-mini",
        "description": "OpenAI GPT-4o Mini",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "openai"
    },
    "gemini-pro": {
        "name": "gemini-pro",
        "description": "Gemini Pro",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "google"
    },
    "gemini-1.5-pro": {
        "name": "gemini-1.5-pro",
        "description": "Gemini 1.5 Pro",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "google"
    },
    "gemini-1.5-flash": {
        "name": "gemini-1.5-flash",
        "description": "Gemini 1.5 Flash",
        "temperature": 0.7,
        "max_tokens": None,
        "provider": "google"
    }
}

DEFAULT_MODEL = "deepseek-v4-flash"

# Game settings
GAME_CONFIG = {
    "player_names": ["Alice", "Bob", "Selena", "Raj"],
}

# Environment settings
ENV_CONFIG = {
    "google_api_key_env": "GOOGLE_API_KEY",
    "openai_api_key_env": "OPENAI_API_KEY",
    "debug_mode": True,
    "log_level": "INFO"
}
