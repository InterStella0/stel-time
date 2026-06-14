from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands


if TYPE_CHECKING:
    from core.types import Context
    from core.bot import StelTime


class ErrorHandlers(commands.Cog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandInvokeError) -> None:
        error = getattr(error, 'original', error)
        if isinstance(error, commands.UserInputError):
            await ctx.send(f"Error: {error}", ephemeral=True)
        else:
            await ctx.send("Something went wrong :/", ephemeral=True)


async def setup(bot: StelTime):
    await bot.add_cog(ErrorHandlers())
