import tomllib
from telethon import TelegramClient

def get_config():
    # See config_template.toml for hints
    config = None
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    return config

def get_client(config) -> TelegramClient:
    api_hash = config["api_hash"]
    api_id = config["api_id"]

    return TelegramClient("stale_members", api_id, api_hash)
