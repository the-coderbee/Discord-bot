from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from guilds.models import Guild
from settings import logging
from utils import checks

logger = logging.getLogger(__name__)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ban', description='Ban a member from server')
    @app_commands.describe(reason="Reason for ban")
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, reason: str = 'Not provided'):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned. Reason: {reason}')

    @commands.hybrid_command(name='kick', description='Kick a member from server')
    @app_commands.describe(reason='Reason for kick')
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, reason: str = 'Not provided'):
        await ctx.send(f'{member.mention} has been kicked. Reason: {reason}')
        await member.kick(reason=reason)

    @commands.hybrid_command(name='timeout', description='Timeout a member on the server')
    @app_commands.describe(time='Amount of time for timeout', reason='Reason for timeout')
    @app_commands.choices(choices=[
        app_commands.Choice(name='Minutes', value='minutes'),
        app_commands.Choice(name='Hours', value='hours'),
        app_commands.Choice(name='Days', value='days'),
    ])
    @commands.has_permissions(administrator=True)
    async def timeout(self, ctx, member: discord.Member, choices: app_commands.Choice[str], time: int,
                      reason: str = 'Not provided'):
        time_delta = datetime.now()
        if choices.value == 'minutes':
            time_delta += timedelta(minutes=time)
        elif choices.value == 'hours':
            time_delta += timedelta(hours=time)
        else:
            time_delta += timedelta(days=time)
        await member.timeout(time_delta, reason=reason)
        await ctx.send(f'*```{member.display_name} has been Timed Out for {time} {choices.value}. Reason: {reason}```*')

    @commands.hybrid_command(name='add_role', description='Give a specific role to a member on the server')
    @app_commands.describe(role='Role you wish to give to the member', reason='Reason for giving role')
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx, member: discord.Member, role: discord.Role, reason: str = 'Not provided'):
        await member.add_roles([role])
        await ctx.send(f'Role {role.mention} has been given to {member.mention}')

    @commands.hybrid_command(name='command_channel', description='Set default channel for bot commands')
    @commands.has_permissions(administrator=True)
    async def set_cmd_chn(self, ctx, channel: discord.TextChannel):
        Guild.set_cmd_channel(ctx.guild.id, channel.id)
        await ctx.send(f'*```Default command channel: Set to {channel}```*')

    @commands.hybrid_command(name='level_webhook_url',
                             description='Set webhook url for level announcements on the server')
    @app_commands.describe(webhook_url='Url of webhook integration for level announcements')
    @commands.has_permissions(administrator=True)
    @checks.is_command_channel()
    async def set_lvl_wh_url(self, ctx, webhook_url: str):
        Guild.set_lvl_wh_url(ctx.guild.id, webhook_url)
        await ctx.send(f'*```Webhook url for level announcements set```*')

    @commands.hybrid_command(name='music_channel', description='Set default channel for music')
    @commands.has_permissions(administrator=True)
    @checks.is_command_channel()
    async def set_music_chn(self, ctx, channel: discord.TextChannel):
        Guild.set_music_channel(ctx.guild.id, channel.id)
        await ctx.send(f'*```Default music command channel: Set to {channel}```*')

    @commands.hybrid_command(name='purge', description='Delete a certain amount of messages on a channel')
    @app_commands.describe(limit='Number of messages you wish to delete (max 100)')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, limit: int = 20, channel: discord.TextChannel = None):
        if limit > 100:
            await ctx.send(f'*```Cannot delete more than 100 messages```*')
            limit = 100
        try:
            channel = channel or ctx.message.channel
        except AttributeError:
            return ctx.send(f'Channel does not exist')
        await ctx.message.delete()
        await channel.purge(limit=limit)
        msg = await ctx.send(f'*```Deleted {limit} messages!```*')
        await msg.delete(delay=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            msg = await ctx.send(f'*```You dont have appropriate permissions```*')
            await msg.delete(delay=5)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
