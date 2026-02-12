# Claude Code Telegram Bot

Remote control for your development environment via Telegram.

## Features

- **Shell execution** - Run any command from your phone
- **Git integration** - Full git workflow (status, commit, push, pull)
- **File operations** - Read files, list directories, view project tree
- **System status** - CPU, memory, disk usage at a glance
- **Security** - Whitelist-based authentication by Telegram user ID
- **Safety guards** - Dangerous commands and destructive git operations are blocked

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 2. Get Your Telegram User ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user ID (a number like `123456789`)

### 3. Configure the Bot

```bash
cd telegram-bot
copy .env.example .env
```

Edit `.env` and fill in:
- `TELEGRAM_BOT_TOKEN` - The token from BotFather
- `ALLOWED_TELEGRAM_IDS` - Your Telegram user ID (comma-separated for multiple users)
- `WORKING_DIR` - Default project directory

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run

```bash
python bot.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Full command reference |
| `/status` | System status (CPU, RAM, disk) |
| `/whoami` | Your Telegram user info |
| `/git <cmd>` | Run git commands |
| `/run <cmd>` | Run shell commands |
| `/read <path>` | Read file content |
| `/ls [path]` | List directory |
| `/tree [depth]` | Directory tree (default depth 2) |
| `/cd <path>` | Change working directory |

## Security

- **Authentication**: Only Telegram user IDs listed in `ALLOWED_TELEGRAM_IDS` can use the bot. Unauthorized users see their ID so they can request access.
- **Blocked commands**: Destructive shell commands (`rm -rf /`, `format`, `shutdown`, etc.) are blocked.
- **Blocked git operations**: `push --force`, `reset --hard`, `clean -f` are blocked. Use the terminal directly for these.
- **Timeout**: Commands are killed after 60 seconds (configurable via `COMMAND_TIMEOUT`).

## Keep Running

### Option A: PM2 (recommended)

```bash
npm install -g pm2
pm2 start bot.py --name telegram-bot --interpreter python
pm2 save
pm2 startup   # auto-start on boot
```

### Option B: Screen / tmux

```bash
screen -S telegram-bot
python bot.py
# Press Ctrl+A, D to detach

# Re-attach later:
screen -r telegram-bot
```

### Option C: Windows Task Scheduler

Create a scheduled task that runs `python bot.py` at startup with the working directory set to the `telegram-bot` folder.

## Project Structure

```
telegram-bot/
  bot.py              Main entry point
  config.py           Configuration constants
  requirements.txt    Python dependencies
  .env.example        Environment variable template
  handlers/
    __init__.py
    commands.py       System and shell commands
    files.py          File read, list, tree
    git.py            Git operations
  utils/
    __init__.py
    auth.py           Telegram user authentication
    executor.py       Async shell command runner
```
