"""
Configuration constants for the Telegram bot.

Values are read from environment variables (.env file) with sensible defaults.
"""

import os

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
ALLOWED_TELEGRAM_IDS: str = os.getenv('ALLOWED_TELEGRAM_IDS', '')

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DEFAULT_WORKING_DIR: str = os.getenv('WORKING_DIR', 'D:/Dev_Projects/Reride')

# ---------------------------------------------------------------------------
# Execution limits
# ---------------------------------------------------------------------------
COMMAND_TIMEOUT: int = int(os.getenv('COMMAND_TIMEOUT', '60'))
MAX_MESSAGE_LENGTH: int = 3800  # Leave room for formatting within Telegram's 4096 limit.

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
