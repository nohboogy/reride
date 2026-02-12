"""
Claude Code Telegram Bot - Main entry point.

Provides remote control of a development environment via Telegram commands.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

from utils.auth import require_auth
from handlers import commands, files
from handlers import git as git_handlers

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=os.getenv('LOG_LEVEL', 'INFO'),
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Top-level command handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with quick-reference commands."""
    await update.message.reply_text(
        "Claude Code Bot\n"
        "\n"
        "Commands:\n"
        "  /help   - Show all commands\n"
        "  /status - System status\n"
        "  /git    - Git operations\n"
        "  /run    - Execute shell command\n"
        "  /read   - Read a file\n"
        "  /ls     - List directory\n"
        "  /tree   - Directory tree\n"
        "  /cd     - Change working dir\n"
        "  /whoami - Your Telegram info\n"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed help text."""
    help_text = (
        "Available Commands\n"
        "\n"
        "--- System ---\n"
        "/start  - Initialize bot\n"
        "/help   - This help message\n"
        "/status - System status (CPU, memory, disk)\n"
        "/whoami - Your Telegram user info\n"
        "\n"
        "--- Git ---\n"
        "/git status        - Working tree status\n"
        "/git log           - Recent commits (last 20)\n"
        "/git diff          - Unstaged changes\n"
        "/git diff --staged - Staged changes\n"
        "/git branch        - List branches\n"
        "/git add <files>   - Stage files\n"
        "/git commit -m \"msg\" - Commit changes\n"
        "/git push          - Push to remote\n"
        "/git pull          - Pull from remote\n"
        "\n"
        "--- Files ---\n"
        "/read <path>   - Read file content\n"
        "/ls [path]     - List directory\n"
        "/tree [depth]  - Directory tree (default depth 2)\n"
        "\n"
        "--- Execution ---\n"
        "/run <command> - Run shell command\n"
        "/cd <path>     - Change working directory\n"
        "\n"
        "--- Security ---\n"
        "Only authorized Telegram user IDs can interact.\n"
        "Dangerous commands (rm -rf /, format, etc.) are blocked.\n"
        "Destructive git operations (push --force, reset --hard) are blocked.\n"
    )
    await update.message.reply_text(help_text)


# ---------------------------------------------------------------------------
# Application bootstrap
# ---------------------------------------------------------------------------
def main():
    """Build the Telegram application and start polling."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Copy .env.example to .env and fill in your bot token."
        )

    app = Application.builder().token(token).build()

    # -- Register handlers --
    # Top-level
    app.add_handler(CommandHandler("start", require_auth(start)))
    app.add_handler(CommandHandler("help", require_auth(help_command)))

    # System
    app.add_handler(CommandHandler("status", require_auth(commands.status)))
    app.add_handler(CommandHandler("whoami", require_auth(commands.whoami)))

    # Git
    app.add_handler(CommandHandler("git", require_auth(git_handlers.git_command)))

    # Files
    app.add_handler(CommandHandler("read", require_auth(files.read_file)))
    app.add_handler(CommandHandler("ls", require_auth(files.list_dir)))
    app.add_handler(CommandHandler("tree", require_auth(files.show_tree)))

    # Execution
    app.add_handler(CommandHandler("run", require_auth(commands.run_command)))
    app.add_handler(CommandHandler("cd", require_auth(commands.change_dir)))

    logger.info("Bot started -- polling for updates")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
