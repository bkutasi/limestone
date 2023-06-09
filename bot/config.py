import yaml
from pathlib import Path

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config
with open(config_dir / "config.yml", "r") as f:
    config_yaml = yaml.safe_load(f)

BACKEND = config_yaml["backend"]
TOKEN = config_yaml["telegram_token"]
BOT_USERNAME = config_yaml["bot_username"]
DEV_ID = config_yaml["developer_id"]
URI = config_yaml["uri"]
USERS = config_yaml["allowed_telegram_usernames"]  # if empty all users are allowed

# chat_modes
with open(config_dir / "chat_personalities.yml", "r", encoding="utf8") as f:
    chat_modes = yaml.safe_load(f)

# instruction templates
with open(config_dir / "instruction_templates.yml", "r", encoding="utf8") as f:
    instruction_templates = yaml.safe_load(f)
