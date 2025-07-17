import logging
import os
import discord
import asyncio

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv

'''
TODO:

1. Move to VPS so I don't have to use 9GB of ram self-hosting a cassandra docker container
2. Join command, adding row in db and granting the user who joined paper money
3. Sell command to allow users to sell their coins
4. Portfolio command to display what the user owns
5. Extra parameter on buy command for either tokens or dollars eg $buy 5 sol token, $buy 500 sol dollar buying 5 sol or $500 worth of sol respectively
6. Admin commands to manually grant people extra money
7. Leverage trading support

'''

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

# Cassandra Setup
cluster = Cluster(["127.0.0.1"], port=9042)
session = cluster.connect()

# Create keyspace and table if they don’t exist
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS exchangebot
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
""")

session.set_keyspace('exchangebot')

session.execute("""
    CREATE TABLE IF NOT EXISTS user_portfolio (
        user_id text,
        symbol text,
        amount double,
        avg_price double,
        last_updated timestamp,
        PRIMARY KEY (user_id, symbol)
    )
""")

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
    bot.cassandra_session = session
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())