import logging
from discord.ext import commands
from database.balance_queries import get_balance, update_balance
from database.leverage_queries import get_position_by_id, close_position
from database.pnl_queries import update_pnl, get_pnl
from utils.cmc_utils import get_price

class Close(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="close")
    async def close_command(self, ctx, position_id: int):
        user_id = str(ctx.author.id)
        position = get_position_by_id(user_id, position_id)

        if not position:
            await ctx.send(f"No open position found with ID `{position_id}`.")
            return

        current_price = get_price(position.symbol)
        entry_price = position.entry_price
        amount = position.amount
        leverage = position.leverage
        is_long = position.is_long

        margin_used = entry_price * amount

        if is_long:
            pnl = (current_price - entry_price) * amount * leverage
        else:
            pnl = (entry_price - current_price) * amount * leverage

        balance = get_balance(user_id)
        old_pnl = get_pnl(user_id)
        update_balance(user_id, balance + margin_used + pnl)
        update_pnl(user_id, old_pnl + pnl)

        close_position(user_id, position_id)

        direction = "LONG" if is_long else "SHORT"
        pnl_sign = "profit" if pnl >= 0 else "loss"

        await ctx.send(
            f"Closed {direction} `{position.symbol}` (ID: `{position_id}`).\n"
            f"Entry: ${entry_price:,.2f} | Exit: ${current_price:,.2f}\n"
            f"PnL: {'+' if pnl >= 0 else ''}${pnl:,.2f} ({pnl_sign})\n"
            f"Amount returned: ${margin_used + pnl:,.2f}\n"
            f"New Balance: ${get_balance(user_id):,.2f}"
        )

async def setup(bot):
    logging.info("Running Close cog setup()")
    await bot.add_cog(Close(bot))
