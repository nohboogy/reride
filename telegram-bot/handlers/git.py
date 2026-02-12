import os
from telegram import Update
from telegram.ext import ContextTypes
from utils.executor import run_shell_command


def _get_working_dir() -> str:
    return os.getenv('WORKING_DIR', 'D:/Dev_Projects/Reride')


# Git subcommands that are always safe (read-only).
SAFE_SUBCOMMANDS = {
    'status', 'log', 'diff', 'branch', 'show', 'remote',
    'tag', 'stash list', 'reflog', 'blame', 'shortlog',
}

# Git subcommands that are blocked for safety.
BLOCKED_SUBCOMMANDS = {
    'push --force', 'push -f',
    'reset --hard',
    'clean -f', 'clean -fd', 'clean -fx',
}


async def git_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute a git command with safety checks."""
    if not context.args:
        help_text = (
            "Git Commands\n"
            "\n"
            "Read-only:\n"
            "  /git status       - Working tree status\n"
            "  /git log          - Recent commits\n"
            "  /git log -5       - Last 5 commits\n"
            "  /git diff         - Unstaged changes\n"
            "  /git diff --staged - Staged changes\n"
            "  /git branch       - List branches\n"
            "  /git remote -v    - Show remotes\n"
            "\n"
            "Write:\n"
            "  /git add <files>  - Stage files\n"
            "  /git commit -m \"msg\" - Commit\n"
            "  /git push         - Push to remote\n"
            "  /git pull         - Pull from remote\n"
            "  /git checkout <b> - Switch branch\n"
            "  /git stash        - Stash changes\n"
            "  /git stash pop    - Apply stash\n"
        )
        await update.message.reply_text(help_text)
        return

    git_args = ' '.join(context.args)

    # Block dangerous commands.
    for blocked in BLOCKED_SUBCOMMANDS:
        if blocked in git_args:
            await update.message.reply_text(
                f"Blocked for safety: git {blocked}\n"
                "Use the terminal directly for destructive operations."
            )
            return

    full_cmd = f'git {git_args}'
    working_dir = _get_working_dir()

    # Add --no-pager to avoid blocking on pager.
    if git_args.startswith(('log', 'diff', 'show', 'blame')):
        full_cmd = f'git --no-pager {git_args}'

    # For log, default to a compact format if no format specified.
    if git_args.strip() == 'log':
        full_cmd = 'git --no-pager log --oneline -20'

    success, output = await run_shell_command(full_cmd, cwd=working_dir)

    if len(output) > 3800:
        output = output[:3800] + "\n\n... (truncated)"

    status_label = "[OK]" if success else "[FAIL]"
    await update.message.reply_text(
        f"{status_label} git {git_args}\n```\n{output}\n```",
        parse_mode='Markdown',
    )
