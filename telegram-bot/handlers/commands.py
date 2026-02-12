import os
import platform
import psutil
from telegram import Update
from telegram.ext import ContextTypes
from utils.executor import run_shell_command

# Mutable working directory state (shared across handlers via env var).
_DEFAULT_WORKING_DIR = 'D:/Dev_Projects/Reride'


def _get_working_dir() -> str:
    return os.getenv('WORKING_DIR', _DEFAULT_WORKING_DIR)


# Commands that are blocked for safety.
BLOCKED_COMMANDS = [
    'rm -rf /',
    'format',
    'del /s /q',
    ':(){',
    'mkfs',
    'dd if=',
    'shutdown',
    'reboot',
]


def _is_blocked(command: str) -> bool:
    """Check if a command matches any blocked pattern."""
    cmd_lower = command.lower().strip()
    return any(blocked in cmd_lower for blocked in BLOCKED_COMMANDS)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system status with resource usage."""
    working_dir = _get_working_dir()

    # Gather system info
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(working_dir)

    status_text = (
        "System Status\n"
        "\n"
        f"Platform: {platform.system()} {platform.release()}\n"
        f"Python: {platform.python_version()}\n"
        f"Working Dir: {working_dir}\n"
        f"User: {os.getenv('USERNAME', os.getenv('USER', 'unknown'))}\n"
        "\n"
        f"CPU: {cpu_percent}%\n"
        f"Memory: {mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)\n"
        f"Disk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)\n"
    )
    await update.message.reply_text(status_text)


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the calling user's Telegram info."""
    user = update.effective_user
    text = (
        "Your Info\n"
        "\n"
        f"Name: {user.full_name}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"ID: {user.id}\n"
        f"Language: {user.language_code or 'N/A'}\n"
    )
    await update.message.reply_text(text)


async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run an arbitrary shell command."""
    if not context.args:
        await update.message.reply_text("Usage: /run <command>")
        return

    command = ' '.join(context.args)

    if _is_blocked(command):
        await update.message.reply_text("Command blocked for safety reasons.")
        return

    working_dir = _get_working_dir()
    await update.message.reply_text(f"Running: {command} ...")

    success, output = await run_shell_command(command, cwd=working_dir)

    # Telegram message limit is 4096 chars.
    if len(output) > 3900:
        output = output[:3900] + "\n\n... (truncated)"

    status_icon = "[OK]" if success else "[FAIL]"
    await update.message.reply_text(f"{status_icon}\n```\n{output}\n```", parse_mode='Markdown')


async def change_dir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the bot's working directory."""
    if not context.args:
        working_dir = _get_working_dir()
        await update.message.reply_text(f"Current directory: {working_dir}")
        return

    new_dir = ' '.join(context.args)

    # Resolve relative paths against the current working directory.
    if not os.path.isabs(new_dir):
        new_dir = os.path.join(_get_working_dir(), new_dir)

    new_dir = os.path.normpath(new_dir)

    if os.path.isdir(new_dir):
        os.environ['WORKING_DIR'] = new_dir
        await update.message.reply_text(f"Changed to: {new_dir}")
    else:
        await update.message.reply_text(f"Directory not found: {new_dir}")
