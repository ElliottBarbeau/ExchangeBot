import logging
import os
import discord
import asyncio

from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from database.table_queries import table_exists
from commands.price import get_price
from tasks.liquidation_monitor import start_monitor
from utils.hl_utils import start_price_feed
from utils.error_utils import get_error_message
from time import sleep

'''
TODO:

Realized pnl by user
Leverage trading support
Move to VPS and secure Cassandra
Reformat to move all spot commands, leverage commands, utils etc into one place

'''

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = ".env"
COGS_PACKAGE = "commands"
COGS_PATH = BASE_DIR / COGS_PACKAGE

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
    activity = discord.Game(name = "with 🦥 in Costa Rica"),
    case_insensitive=True
)

# Cog loader
async def load_cogs():
    for file in COGS_PATH.iterdir():
        if not file.name.startswith("_") and file.name.endswith(".py"):
            ext = f"{COGS_PACKAGE}.{file.stem}"  # e.g. "commands.buy"
            try:
                await bot.load_extension(ext)
                logging.info("Loaded extension: %s", ext)
            except commands.ExtensionAlreadyLoaded:
                logging.warning("Extension %s already loaded", ext)
            except Exception as exc:
                logging.exception("Failed to load %s: %s", ext, exc)

# Global events
@bot.event
async def on_ready():
    print("All commands:", sorted(bot.all_commands.keys()))
    start_price_feed(bot.loop)
    start_monitor(bot)
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
    
    error_message = get_error_message(ctx.command.cog_name.lower())
    logging.error("Error in command %s: %s", ctx.command.cog_name, error)
    await ctx.reply(f"Oops! {error_message}", mention_author=False)
    

async def main() -> None:
    bot.initialized = False if not table_exists('exchangebot', 'user_portfolio') else True
    bot.prices = {}
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())