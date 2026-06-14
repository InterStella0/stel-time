import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from core.db import Database


VERSION = '0.0.1'

class StelTime(commands.Bot):
    def __init__(self):
        self.db: Database = Database()
        intents = discord.Intents.none()
        installs = app_commands.AppInstallationType(user=True)
        allowed_contexts = app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
        super().__init__("uwu", intents=intents, allowed_installs=installs, allowed_contexts=allowed_contexts)

    async def setup_hook(self) -> None:
        await self.db.setup()
        await self.load_extension('cogs.error_handlers')
        await self.load_extension('cogs.commands')
        if await self.db.get_synced_version() != VERSION:
            logging.info("syncing...")
            await self.tree.sync()
            await self.db.set_synced_version(VERSION)
            logging.info("synced globally")
        else:
            logging.info("skipping sync, version unchanged")

        logging.info(f"Bot version: {VERSION}")

    def running(self):
        try:
            self.run(os.environ['TOKEN'], root_logger=True)
        except KeyError:
            logging.error("You need to set a discord token in .env file.")
