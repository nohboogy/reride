import os
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _get_allowed_ids() -> list[int]:
    """Parse allowed user IDs from environment variable."""
    raw = os.getenv('ALLOWED_TELEGRAM_IDS', '')
    ids = []
    for uid in raw.split(','):
        uid = uid.strip()
        if uid:
            try:
                ids.append(int(uid))
            except ValueError:
                logger.warning("Invalid user ID in ALLOWED_TELEGRAM_IDS: %s", uid)
    return ids


ALLOWED_USER_IDS = _get_allowed_ids()


def require_auth(func):
    """Decorator to require authentication via Telegram user ID whitelist."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user is None:
            return

        if user.id not in ALLOWED_USER_IDS:
            logger.warning(
                "Unauthorized access attempt by user %s (ID: %d)",
                user.full_name, user.id
            )
            await update.message.reply_text(
                "Unauthorized. Your Telegram ID: {}\n"
                "Contact the bot admin to get whitelisted.".format(user.id)
            )
            return

        return await func(update, context)
    return wrapper
