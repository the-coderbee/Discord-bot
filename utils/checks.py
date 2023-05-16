import discord
from discord.ext import commands
from guilds.models import Guild


class NotCmdChannel(commands.CheckFailure):
    error_msg = f'*```This is not the default channel for commands.```*'


class DefaultNotSet(commands.CheckFailure):
    error_msg = f'*```No default channel for commands. Set a default channel first. Type \'/help\'.```*'


class NotMusicChannel(commands.CheckFailure):
    channel: int = None
    error_msg = f'*```This is not the default channel for music commands.```*'


class MusicDefaultNotSet(commands.CheckFailure):
    error_msg = f'*```No default channel for music. Set a default channel first. Type \'/help\'.```*'


def is_command_channel():
    async def predicate(ctx):
        cmd_channel_id = Guild.get_cmd_channel(ctx.guild.id)
        if not cmd_channel_id:
            raise DefaultNotSet
        elif ctx.message.channel.id != int(cmd_channel_id):
            raise NotCmdChannel
        return True
    return commands.check(predicate)


def is_music_channel():
    async def predicate(ctx):
        music_channel_id = Guild.get_music_channel(ctx.guild.id)
        if not music_channel_id:
            raise DefaultNotSet
        elif ctx.message.channel.id != int(music_channel_id):
            NotMusicChannel.set_channel(music_channel_id)
            raise NotCmdChannel
        return True
    return commands.check(predicate)
