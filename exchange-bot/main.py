import logging
import os
import discord

from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = ".env"
COMMANDS_DIR = "commands"
COGS_PACKAGE = "commands"
COGS_PATH = BASE_DIR / COMMANDS_DIR

# Load dotenv for discord token
load_dotenv(BASE_DIR / ENV_FILE)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise RuntimeError("DISCORD_TOKEN not found in env file.")

# Initialize logging
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(
    command_prefix = "$",
    intents = intents,
    help_command = commands.MinimalHelpCommand(),
    activity = discord.Game(name = "with Python 🐍"),
    case_insensitive=True
)

# Cog loader
def load_cogs():
    for file in COGS_PATH.iterdir():
        if not file.name.startswith("_") and file.name.endswith(".py"):
            ext = f"{COGS_PACKAGE}.{file.stem}"  # e.g. "commands.buy"
            try:
                bot.load_extension(ext)
                logging.info("Loaded extension: %s", ext)
            except commands.ExtensionAlreadyLoaded:
                logging.warning("Extension %s already loaded", ext)
            except Exception as exc:
                logging.exception("Failed to load %s: %s", ext, exc)

# Global events

@bot.event
async def on_ready():
    print("All commands:", bot.all_commands.keys())
    logging.info(
        "Logged in as %s (ID: %s). Connected to %d guild(s).",
        bot.user,
        bot.user.id,
        len(bot.guilds),
    )

# Error handling

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return
    logging.error("Error in command %s: %s", ctx.command, error)
    await ctx.reply(f"Oops! {error}", mention_author=False)

def main() -> None:
    load_cogs()
    bot.run(TOKEN, reconnect = True)

if __name__ == "__main__":
    main()