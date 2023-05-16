import sys
import traceback

import discord
from discord.ext import commands

from classes.bot import GookyBot
from database.database import db
from guilds.models import Guild
from levelsystem.models import UserActivity
from settings import logging, BOT_TOKEN
from users.models import User
from utils import checks

logger = logging.getLogger('bot')


def create_table():
    db.create_tables([Guild, User, UserActivity])


def run():
    create_table()
    intents = discord.Intents.all()
    bot = GookyBot(command_prefix='-', intents=intents)
    bot.initialise()

    @bot.event
    async def on_ready():
        logging.info(f'{bot.user} (ID: {bot.user.id}) is READY')
        await bot.load_extension('cogs.levelling')
        await bot.load_extension('cogs.moderation')
        await bot.load_extension('cogs.welcome')
        # await bot.load_extension('cogs.music')
        await bot.tree.sync()

    @bot.event
    async def on_message(message: discord.Message):
        url = Guild.get_lvl_wh_url(message.guild.id)
        if not url and message.author == message.guild.owner:
            await message.channel.send(f'Reminder: \t*```Webhook for level announcements not set```*')
        ctx = await bot.get_context(message)
        if not ctx.valid:
            if not message.author.bot:
                await bot.process_message(message)
        await bot.process_commands(message)

    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        await bot.process_reaction(payload)

    @bot.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
        await bot.process_reaction(payload)

    @bot.listen()
    async def on_command_error(ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = ()

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.CommandNotFound):
            text = f'*```Sorry {ctx.author.mention}, you tried an invalid command. ' \
                   f'Type "{bot.command_prefix}help" for a detailed list of commands.```*'
            msg = await ctx.send(text)
            await msg.delete(delay=10)

        elif isinstance(error, checks.NotCmdChannel):
            msg = await ctx.send(checks.NotCmdChannel.error_msg)
            await msg.delete(delay=10)

        elif isinstance(error, checks.DefaultNotSet):
            msg = await ctx.send(checks.DefaultNotSet.error_msg)
            await msg.delete(delay=10)

        elif isinstance(error, commands.DisabledCommand):
            msg = await ctx.send(f'*```{ctx.command} has been disabled.```*')
            await msg.delete(delay=10)

        elif isinstance(error, commands.MissingPermissions):
            msg = await ctx.send(f'*```You dont have appropriate permissions```*')
            await msg.delete(delay=10)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                msg = await ctx.author.send(f'*```{ctx.command} can not be used in Private Messages.```*')
                await msg.delete(delay=10)
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                msg = await ctx.send(f'*```I could not find that member. Please try again.```*')
                await msg.delete(delay=10)

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    bot.run(BOT_TOKEN, root_logger=True)


if __name__ == '__main__':
    run()
