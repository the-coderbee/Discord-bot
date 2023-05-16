import discord

from classes.models import BaseModel
from peewee import *
from guilds.models import Guild


class User(BaseModel):
    user_id = CharField(max_length=100)
    guild = ForeignKeyField(model=Guild)
    total_xp = FloatField(default=0)

    @staticmethod
    def fetch_user_and_guild_by_id(user_id: int, guild_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        try:
            user = User.get(User.user_id == user_id, User.guild == guild)
        except DoesNotExist:
            user = User.create(user_id=user_id, guild=guild)
        return user, guild

    @staticmethod
    def get_leaderboard(users_num: int, guild_id: int):
        return User.select().join(Guild).where(
            Guild.guild_id == guild_id).order_by(User.total_xp.desc())[:users_num]

    @staticmethod
    def get_rank_from_leaderboard(member: discord.Member, guild_id: int) -> int:
        leaderboard = User.select().join(Guild).where(
            Guild.guild_id == guild_id).order_by(User.total_xp.desc())
        lst = []
        for user in leaderboard:
            lst.append(user.user_id)
        for index, user_id in enumerate(lst):
            if int(user_id) == member.id:
                rank = index + 1
                return rank
