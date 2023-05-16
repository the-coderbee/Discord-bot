import discord
from discord.ext import commands

from classes.bot_handler import BotHandler
from levelsystem.level_controller import Levels
from mesengers.discord_messenger import DiscordMessenger


class GookyBot(commands.Bot):
    levels: Levels

    def initialise(self):
        messenger = DiscordMessenger()
        bot_handler = BotHandler(self)
        self.levels = Levels(messenger, bot_handler)

    async def process_message(self, message: discord.Message):
        await self.levels.process_message(message)

    async def process_reaction(self, payload: discord.RawReactionActionEvent):
        await self.levels.process_reaction(payload)
