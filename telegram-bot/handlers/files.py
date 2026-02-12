import os
from telegram import Update
from telegram.ext import ContextTypes


def _get_working_dir() -> str:
    return os.getenv('WORKING_DIR', 'D:/Dev_Projects/Reride')


def _resolve_path(path: str) -> str:
    """Resolve a path relative to the working directory."""
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(_get_working_dir(), path))


async def read_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Read and display the contents of a file."""
    if not context.args:
        await update.message.reply_text("Usage: /read <path>")
        return

    file_path = ' '.join(context.args)
    full_path = _resolve_path(file_path)

    if not os.path.isfile(full_path):
        await update.message.reply_text(f"File not found: {full_path}")
        return

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content:
            await update.message.reply_text(f"{file_path} (empty file)")
            return

        # Telegram message limit is 4096 chars; leave room for header + formatting.
        if len(content) > 3800:
            content = content[:3800] + "\n\n... (truncated)"

        await update.message.reply_text(
            f"{file_path}\n```\n{content}\n```",
            parse_mode='Markdown',
        )
    except UnicodeDecodeError:
        size = os.path.getsize(full_path)
        await update.message.reply_text(
            f"Binary file: {file_path} ({size} bytes). Cannot display."
        )
    except Exception as e:
        await update.message.reply_text(f"Error reading file: {e}")


async def list_dir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List directory contents with type indicators."""
    path = ' '.join(context.args) if context.args else '.'
    full_path = _resolve_path(path)

    if not os.path.isdir(full_path):
        await update.message.reply_text(f"Not a directory: {full_path}")
        return

    try:
        items = sorted(os.listdir(full_path))

        if not items:
            await update.message.reply_text(f"{path}/ (empty)")
            return

        lines = []
        for item in items:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                lines.append(f"[DIR]  {item}/")
            else:
                size = os.path.getsize(item_path)
                if size >= 1024 * 1024:
                    size_str = f"{size / (1024*1024):.1f}MB"
                elif size >= 1024:
                    size_str = f"{size / 1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                lines.append(f"[FILE] {item} ({size_str})")

        output = "\n".join(lines)

        if len(output) > 3800:
            output = output[:3800] + "\n\n... (truncated)"

        await update.message.reply_text(
            f"{path}/\n```\n{output}\n```",
            parse_mode='Markdown',
        )
    except PermissionError:
        await update.message.reply_text(f"Permission denied: {full_path}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def show_tree(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a directory tree up to a given depth."""
    depth = 2
    if context.args:
        try:
            depth = int(context.args[0])
            depth = min(depth, 5)  # Cap at 5 to avoid huge output.
        except ValueError:
            await update.message.reply_text("Usage: /tree [depth]  (depth is a number, default 2)")
            return

    working_dir = _get_working_dir()

    # Directories/files to skip.
    SKIP = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        '.env', '.idea', '.vscode', 'dist', 'build', '.next',
    }

    def build_tree(path: str, prefix: str = "", depth_left: int = depth) -> list[str]:
        if depth_left <= 0:
            return []

        lines = []
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return [f"{prefix}(permission denied)"]

        # Filter out skipped items.
        items = [i for i in items if i not in SKIP and not i.startswith('.')]

        for idx, item in enumerate(items):
            full = os.path.join(path, item)
            is_last = idx == len(items) - 1
            connector = "└── " if is_last else "├── "

            if os.path.isdir(full):
                lines.append(f"{prefix}{connector}{item}/")
                extension = "    " if is_last else "│   "
                lines.extend(build_tree(full, prefix + extension, depth_left - 1))
            else:
                lines.append(f"{prefix}{connector}{item}")

        return lines

    try:
        tree_lines = build_tree(working_dir)

        if not tree_lines:
            await update.message.reply_text("(empty or all items filtered)")
            return

        output = "\n".join(tree_lines)

        if len(output) > 3800:
            output = output[:3800] + "\n\n... (truncated)"

        header = os.path.basename(working_dir) + "/"
        await update.message.reply_text(
            f"```\n{header}\n{output}\n```",
            parse_mode='Markdown',
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
