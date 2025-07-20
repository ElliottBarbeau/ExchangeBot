import logging
import discord

from discord.ext import commands
from database.portfolio_queries import get_full_portfolio
from database.leverage_queries import get_leverage_portfolio
from utils.cmc_utils import get_price
from collections import defaultdict

class Port(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="port")
    async def portfolio_command(self, ctx):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        user_id = str(ctx.author.id)

        spot_portfolio = get_full_portfolio(user_id)
        leverage_positions = get_leverage_portfolio(user_id)

        if not spot_portfolio and not leverage_positions:
            await ctx.send("Portfolio empty. Use $buy to purchase something first!")
            return
        
        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Portfolio",
            color = discord.Color.gold()
        )

        prices = defaultdict(float)
        total_positions = 0
        pnl, total_cost, total_value = 0, 0, 0
        for row in spot_portfolio:
            symbol = row.symbol.upper()
            amount = row.amount
            cost = row.avg_price * amount

            if symbol not in prices:
                prices[symbol] = get_price(symbol)

            value = prices[symbol] * amount

            if value < 1:
                continue

            total_cost += cost
            total_value += value
            avg_price = row.avg_price
            raw_pnl = value - cost
            pnl += raw_pnl

            embed.add_field(
                name = f"💠 {symbol}",
                value=f"Amount: `{amount:,.4f}`\n"
                      f"Avg Price: `${avg_price:,.2f}`\n"
                      f"Value: `${value:,.2f}`\n"
                      f"Cost: `${cost:,.2f}`\n"
                      f"PnL: `{'+' if raw_pnl >= 0 else ''}{raw_pnl:,.2f}`",
                inline=False
            )
            total_positions += 1

        for pos in leverage_positions:
            symbol = pos.symbol.upper()
            amount = pos.amount
            entry_price = pos.entry_price
            leverage = pos.leverage
            is_long = pos.is_long
            position_id = pos.position_id
            liquidation_price = pos.liquidation_price
            current_price = get_price(symbol)
            direction = "LONG" if is_long else "SHORT"

            # Notional value - your total position size with leverage
            notional_value = abs(current_price * amount) * leverage
            notional_amount = amount * leverage

            # PnL with new leverage factored in
            raw_pnl = (current_price - pos.entry_price) * pos.amount * leverage
            if not pos.is_long:
                raw_pnl = -raw_pnl

            total_value += notional_value

            max_loss = -(amount * entry_price)
            raw_pnl = max(raw_pnl, max_loss)
            pnl += raw_pnl

            embed.add_field(
                name=f"⚡ #{position_id} {symbol} ({direction} {leverage:,.2f}x)",
                value=f"Position Size: `{notional_amount:,.4f}`\n"
                    f"Entry: `${entry_price:,.2f}`\n"
                    f"Current: `${current_price:,.2f}`\n"
                    f"Liquidation Price: `${liquidation_price:,.2f}`\n"
                    f"PnL: `{'+' if raw_pnl >= 0 else ''}{raw_pnl:,.2f}{' - Liquidation Pending' if raw_pnl == max_loss else ''}`",
                inline=False
            )
            total_positions += 1

        pnl_sign = "📈" if pnl >= 0 else "📉"
        embed.add_field(
            name="Portfolio Summary",
            value=f"Total Value: `${total_value:,.2f}`\n"
                    f"PnL: {pnl_sign} `${pnl:,.2f}`",
            inline=False
        )

        embed.set_footer(text=f"Total positions: {total_positions}")
        await ctx.send(embed=embed)

async def setup(bot):
    logging.info("Running Port cog setup()")
    await bot.add_cog(Port(bot))