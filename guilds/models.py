from peewee import *

from classes.models import BaseModel


class Guild(BaseModel):
    guild_id = CharField(max_length=100, primary_key=True)
    cmd_channel_id = CharField(max_length=100, null=True)
    level_webhook_url = CharField(max_length=200, null=True)
    music_channel_id = CharField(max_length=100, null=True)

    @staticmethod
    def fetch_guild_by_id(guild_id: int):
        try:
            guild = Guild.get(Guild.guild_id == guild_id)
        except DoesNotExist:
            guild = Guild.create(guild_id=guild_id)

        return guild

    @staticmethod
    def set_cmd_channel(guild_id: int, channel_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        guild.cmd_channel_id = channel_id
        guild.save()

    @staticmethod
    def get_cmd_channel(guild_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        if guild.cmd_channel_id:
            return guild.cmd_channel_id
        else:
            return None

    @staticmethod
    def set_lvl_wh_url(guild_id: int, webhook_url: str):
        guild = Guild.fetch_guild_by_id(guild_id)
        guild.level_webhook_url = webhook_url
        guild.save()

    @staticmethod
    def get_lvl_wh_url(guild_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        if guild.level_webhook_url:
            return guild.level_webhook_url
        else:
            return None

    @staticmethod
    def set_music_channel(guild_id: int, channel_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        guild.music_channel_id = channel_id
        guild.save()

    @staticmethod
    def get_music_channel(guild_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        if guild.music_channel_id:
            return guild.music_channel_id
        else:
            return None
