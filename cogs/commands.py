from __future__ import annotations
import re
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

import discord
from discord import app_commands, DMChannel
from discord.ext import commands
from rapidfuzz import process
from zoneinfo import ZoneInfo, available_timezones

from core.errors import UserError
from core.utils import parse_utc_offset, get_timezones, get_timezones_by_offset


if TYPE_CHECKING:
    from core.types import Interaction, Context

class Commands(commands.Cog):
    @commands.hybrid_command()
    async def time(self, ctx: Context):
        """Shows your friend's time."""
        channel = ctx.channel
        if channel.guild is not None:
            raise

        assert isinstance(channel, DMChannel)
        resolved_user = channel.recipient
        assert resolved_user is not None
        if (timezone_data := await ctx.bot.db.fetch_user(resolved_user.id)) is None:
            raise UserError("User has no timezone being set.")

        if timezone_data.timezone is not None:
            tz = ZoneInfo(timezone_data.timezone)
            now = datetime.now(tz=tz)
            label = timezone_data.timezone
        else:
            offset = timezone_data.offset
            assert offset is not None
            offset_td = timedelta(hours=offset)
            tz = timezone(offset_td)
            now = datetime.now(tz=tz)
            total_minutes = int(offset_td.total_seconds() // 60)
            sign = '+' if total_minutes >= 0 else '-'
            h, m = divmod(abs(total_minutes), 60)
            label = f"UTC{sign}{h:02}:{m:02}"

        formatted = now.strftime("%I:%M %p %A %d %b %Y")
        await ctx.send(f"Time: **{formatted}** (`{label}`)", ephemeral=True)

    @commands.hybrid_group(name="timezone", fallback="profile")
    async def timezone_command(self, ctx: Context):
        """Tells you the current timezone for this user."""
        channel = ctx.channel
        if channel.guild is not None:
            raise

        assert isinstance(channel, DMChannel)
        resolved_user = channel.recipient
        assert resolved_user is not None
        if (timezone_data := await ctx.bot.db.fetch_user(resolved_user.id)) is None:
            raise UserError("User has no timezone being set.")

        embed = discord.Embed()
        if timezone_data.timezone:
            embed.add_field(name="Timezone", value=timezone_data.timezone)
        if timezone_data.offset:
            offset_td = timedelta(hours=timezone_data.offset)
            total_minutes = int(offset_td.total_seconds() // 60)
            sign = '+' if total_minutes >= 0 else '-'
            h, m = divmod(abs(total_minutes), 60)
            label = f"UTC{sign}{h:02}:{m:02}"
            embed.add_field(name="From GMT", value=label)

        await ctx.send(embed=embed, ephemeral=True)

    @timezone_command.command(name="set")
    async def command_set(self, ctx: Context, timezone: str):
        """Set time zone of a user."""
        channel = ctx.channel
        if channel.guild is not None:
            raise

        assert isinstance(channel, DMChannel)
        resolved_user = channel.recipient
        assert resolved_user is not None
        offset = parse_utc_offset(timezone)
        if offset is None:
            m = re.match(r'^UTC([+-])(\d{2}):(\d{2})$', timezone)
            if m:
                sign = 1 if m.group(1) == '+' else -1
                offset = timedelta(hours=sign * int(m.group(2)), minutes=sign * int(m.group(3)))

        if offset is not None:
            await ctx.bot.db.set_offset(resolved_user.id, offset.total_seconds() / 3600)
            await ctx.send("Timezone offset saved.", ephemeral=True)
        elif timezone in available_timezones():
            await ctx.bot.db.set_timezone(resolved_user.id, timezone)
            await ctx.send(f"Timezone set to {timezone}.", ephemeral=True)
        else:
            raise UserError(f"`{timezone}` is not a recognised timezone.")

    @timezone_command.command(name="delete", description="Remove time zone of a user.")
    async def command_remove(self, ctx: Context):
        """Remove timezone set for a user."""
        channel = ctx.channel
        if channel.guild is not None:
            raise

        assert isinstance(channel, DMChannel)
        resolved_user = channel.recipient
        assert resolved_user is not None
        await ctx.bot.db.delete_user(resolved_user.id)
        await ctx.send("Timezone removed.", ephemeral=True)

    @command_set.autocomplete('timezone')
    async def autocomplete_callback(self, _: Interaction, current: str):
        """Find a time zone, i.e. Asia/Kuala_Lumpur or UTC+1:00"""
        find = current.strip()

        if (offset := parse_utc_offset(find)) is not None:
            total_minutes = int(offset.total_seconds() // 60)
            sign = '+' if total_minutes >= 0 else '-'
            h, m = divmod(abs(total_minutes), 60)
            literal = f"UTC{sign}{h:02}:{m:02}"
            tz_choices = [app_commands.Choice(name=tz, value=tz) for tz in get_timezones_by_offset(offset)[:14]]
            return [app_commands.Choice(name=literal, value=literal), *tz_choices]
        elif find == "":
            selections = get_timezones()[:15]
        else:
            selections = process.extract(find, get_timezones(), limit=15)
            selections = [choice for choice, *_ in selections]

        return [app_commands.Choice(name=choice, value=choice) for choice in selections]


async def setup(bot):
    await bot.add_cog(Commands())
