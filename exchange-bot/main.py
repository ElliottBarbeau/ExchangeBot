import logging
import os
import discord
import asyncio

from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv
from database.table_queries import table_exists

'''
TODO:

Add user balance to table
$Start command for bot to create table so it isn't checking to create table every time the main.py file is launched
$Join command, adding row in db and granting the user who joined paper money
$Sell command to allow users to sell their coins
$Fill command to give the user extra money
Move to VPS and secure Cassandra
Portfolio command to display what the user owns
Extra parameter on buy command for either tokens or dollars eg $buy 5 sol token, $buy 500 sol dollar buying 5 sol or $500 worth of sol respectively
Admin commands to manually grant people extra money
Leverage trading support

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
    activity = discord.Game(name = "with Python 🐍"),
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

async def main() -> None:
    bot.initialized = False if not table_exists('exchangebot', 'user_portfolio') else True
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())