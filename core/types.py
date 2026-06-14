import discord
from discord.ext import commands

from core.bot import StelTime

Interaction = discord.Interaction[StelTime]
Context = commands.Context[StelTime]