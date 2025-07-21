import os
from dotenv import load_dotenv
from discord.ext import tasks
from discord import Embed
from database.leverage_queries import get_leverage_portfolio, close_position, get_all_user_ids_with_positions
from database.pnl_queries import update_pnl, get_pnl
from utils.hl_utils import get_price

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@tasks.loop(minutes=15)
async def monitor_liquidations():
    print("Running liquidation monitor")
    bot = monitor_liquidations.bot
    channel = bot.get_channel(CHANNEL_ID)
    all_users = get_all_user_ids_with_positions()

    for user_id in all_users:
        positions = get_leverage_portfolio(user_id)

        for pos in positions:
            current_price = get_price(pos.symbol)
            liq_price = pos.liquidation_price

            margin = pos.amount * pos.entry_price
            pnl = get_pnl(user_id)
            new_pnl = pnl - margin

            if pos.is_long:
                if current_price <= liq_price:
                    close_position(user_id, pos.position_id)
                    update_pnl(user_id, new_pnl)

                    embed = Embed(
                        title="💥 Liquidation Alert",
                        description=(
                            f"<@{user_id}> got liquidated on **LONG** `{pos.symbol}`!\n"
                            f"Entry Price: ${pos.entry_price:,.2f}\n"
                            f"Liquidation Price: ${liq_price:,.2f}\n"
                            f"Current Price: ${current_price:,.2f}\n"
                            f"Leverage: {pos.leverage}x"
                        ),
                        color=0xFF0000
                    )
                    if channel:
                        await channel.send(embed=embed)
                    print(f"Liquidated LONG position for user {user_id} on {pos.symbol}")

            else:
                if current_price >= liq_price:
                    close_position(user_id, pos.position_id)
                    update_pnl(user_id, new_pnl)

                    embed = Embed(
                        title="💥 Liquidation Alert",
                        description=(
                            f"<@{user_id}> got liquidated on **SHORT** `{pos.symbol}`!\n"
                            f"Entry Price: ${pos.entry_price:,.2f}\n"
                            f"Liquidation Price: ${liq_price:,.2f}\n"
                            f"Current Price: ${current_price:,.2f}\n"
                            f"Leverage: {pos.leverage}x"
                        ),
                        color=0xFF0000
                    )
                    if channel:
                        await channel.send(embed=embed)
                    print(f"Liquidated SHORT position for user {user_id} on {pos.symbol}")

def start_monitor(bot):
    monitor_liquidations.bot = bot
    monitor_liquidations.start()
    print(f"{bot.user} is online, liquidation monitor running.")
