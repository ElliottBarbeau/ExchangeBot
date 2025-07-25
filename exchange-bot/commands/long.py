import logging
import math
from discord.ext import commands
from database.balance_queries import get_balance, update_balance
from database.leverage_queries import open_position, get_existing_position, update_position
from utils.leverage_utils import get_maintenance_margin_ratio, calculate_liquidation_price_long
from utils.hl_utils import get_price

MAX_LEVERAGE = 100

class Long(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="long")
    async def long_command(self, ctx, symbol: str, amount: str, leverage: float):
        if leverage <= 0 or leverage > MAX_LEVERAGE:
            await ctx.send(f"Leverage must be between 1 and {MAX_LEVERAGE}x.")
            return

        user_id = str(ctx.author.id)
        balance = get_balance(user_id)

        if balance is None:
            await ctx.send("User has not joined the game. Type $join to get started!")
            return
        
        symbol = symbol.upper()
        price = await get_price(symbol)
        

        # If amount starts with '$' => dollar amount
        if amount.startswith('$'):
            try:
                dollar_amount = float(amount[1:])
                token_amount = dollar_amount / price
            except ValueError:
                await ctx.send("Invalid dollar amount format.")
                return
        else:
            try:
                token_amount = float(amount)
            except ValueError:
                await ctx.send("Invalid token amount format.")
                return
            
        if token_amount <= 0 or math.isnan(token_amount):
            await ctx.send(f"Amount must be greater than 0.")
            return

        required_margin = price * token_amount

        if balance < required_margin:
            await ctx.send(f"Not enough balance. You need at least ${required_margin:,.4f} to open this position.")
            return

        update_balance(user_id, balance - required_margin)
        
        existing = get_existing_position(user_id, symbol, is_long=True)

        if existing:
            combined_amount = existing.amount + token_amount
            new_entry = ((existing.entry_price * existing.amount) + (price * token_amount)) / combined_amount

            old_margin = existing.entry_price * existing.amount
            new_margin = price * token_amount
            total_margin = old_margin + new_margin

            old_notional = existing.entry_price * existing.amount * existing.leverage
            new_notional = price * token_amount * leverage
            combined_notional = old_notional + new_notional

            new_leverage = combined_notional / total_margin

            maintenance_margin_ratio = get_maintenance_margin_ratio(new_leverage)

            new_liq = calculate_liquidation_price_long(
                entry_price=new_entry,
                margin=total_margin,
                amount=combined_amount,
                leverage=new_leverage,
                maintenance_margin_ratio=maintenance_margin_ratio
            )

            update_position(
                user_id=user_id,
                position_id=existing.position_id,
                amount=combined_amount,
                entry_price=new_entry,
                leverage=new_leverage,
                liq_price=new_liq
            )

            await ctx.send(f"Added to existing LONG position on {symbol.upper()}.\n"
                           f"New Size: {combined_amount * new_leverage:,.4f} {symbol} (Notional) @ Avg ${new_entry:,.4f}\n"
                           f"New Liquidation Price: ${new_liq:,.4f}")
            
        else:
            
            maintenance_margin_ratio = get_maintenance_margin_ratio(leverage)
            margin = price * token_amount

            liq_price = calculate_liquidation_price_long(
                entry_price=price,
                margin=margin,
                amount=token_amount,
                leverage=leverage,
                maintenance_margin_ratio=maintenance_margin_ratio
            )

            open_position(
                user_id=user_id,
                symbol=symbol,
                amount=token_amount,
                entry_price=price,
                leverage=leverage,
                liq_price=liq_price,
                is_long=True
            )

            await ctx.send(f"Opened LONG with notional size {token_amount * leverage:,.4f} {symbol.upper()} @ ${price:,.4f} "
                        f"with {leverage}x leverage.\n"
                        f"Liquidation Price: ${liq_price:,.4f}")

async def setup(bot):
    logging.info("Running Long cog setup()")
    await bot.add_cog(Long(bot))
