import os
from dotenv import load_dotenv
from discord.ext import tasks
from discord import Embed
from database.leverage_queries import get_leverage_portfolio, close_position, get_all_user_ids_with_positions
from database.balance_queries import get_balance, update_balance
from utils.cmc_utils import get_price
from utils.leverage_utils import get_maintenance_margin_ratio, calculate_liquidation_price_long, calculate_liquidation_price_short

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@tasks.loop(minutes=15)
async def monitor_liquidations():
    bot = monitor_liquidations.bot
    channel = bot.get_channel(CHANNEL_ID)
    all_users = get_all_user_ids_with_positions()

    for user_id in all_users:
        balance = get_balance(user_id)
        positions = get_leverage_portfolio(user_id)

        for pos in positions:
            current_price = get_price(pos.symbol)
            maintenance_margin_ratio = get_maintenance_margin_ratio(pos.leverage)

            if pos.is_long:
                liq_price = calculate_liquidation_price_long(
                    pos.entry_price,
                    pos.leverage,
                    maintenance_margin_ratio
                )

                if current_price <= liq_price:
                    close_position(user_id, pos.position_id)

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
                liq_price = calculate_liquidation_price_short(
                    pos.entry_price,
                    pos.leverage,
                    maintenance_margin_ratio
                )
                if current_price >= liq_price:
                    close_position(user_id, pos.position_id)

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
