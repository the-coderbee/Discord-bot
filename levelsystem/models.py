import math
from enum import Enum

from peewee import *

from classes.models import BaseModel
from guilds.models import Guild
from users.models import User


class XpType(Enum):
    MESSAGE = 8
    REACTION = 2
    VOICE = 6
    MANUAL = 0


class LevelModel:
    # xp = (level / x) ** y is the formula
    @staticmethod
    def get_level_from_xp(xp: float) -> int:
        return math.floor(math.sqrt(xp) * 0.25)

    @staticmethod
    def get_xp_from_level(level: int) -> float:
        return (level / 0.25) ** 2

    @staticmethod
    def level_changed(current_xp: float, new_xp: float):
        changed = False
        current_lvl = LevelModel.get_level_from_xp(current_xp)
        new_lvl = LevelModel.get_level_from_xp(new_xp)
        if current_lvl != new_lvl:
            changed = True
        return changed, current_lvl, new_lvl

    @staticmethod
    def current_level_gap(current_xp: float):
        current_lvl = LevelModel.get_level_from_xp(current_xp)
        current_lvl_xp = LevelModel.get_xp_from_level(current_lvl)
        next_level_xp = LevelModel.get_xp_from_level(current_lvl + 1)
        progress = current_xp - current_lvl_xp
        return next_level_xp - current_lvl_xp, progress


class UserActivity(BaseModel):
    MODE_ADD = 'ADD'
    MODE_REDUCE = 'REDUCE'
    MODE_CHOICES = (
        (MODE_ADD, MODE_ADD),
        (MODE_REDUCE, MODE_REDUCE)
    )

    user = ForeignKeyField(model=User)
    message_id = CharField(max_length=100)
    guild_id = CharField(max_length=100)
    xp = FloatField()
    mode = CharField(choices=MODE_CHOICES, default=MODE_ADD)
    is_reaction = BooleanField(default=False)

    def save_new_recorded_xp(self, xp_type: XpType, mode, manual_xp: float, modifier: float):
        xp = xp_type.value
        if xp_type == XpType.REACTION:
            self.is_reaction = True
        xp *= modifier
        if xp_type == XpType.MANUAL:
            xp = manual_xp

        current_total_xp = UserActivity.get_total_xp(self.user.user_id, self.guild_id)
        if mode == UserActivity.MODE_ADD:
            new_total_xp = current_total_xp + xp
        else:
            new_total_xp = current_total_xp - xp
        self.user.total_xp = new_total_xp
        self.user.save()

        self.xp = xp
        self.mode = mode
        self.save()

        return LevelModel.level_changed(current_total_xp, new_total_xp)

    @staticmethod
    def get_total_xp(user_id: int, guild_id: int):
        guild = Guild.fetch_guild_by_id(guild_id)
        xp_added = (
            UserActivity.select(fn.SUM(UserActivity.xp).alias("total"))
            .join(User)
            .where(User.user_id == str(user_id), User.guild == guild, UserActivity.mode == UserActivity.MODE_ADD)
        )
        xp_reduced = (
            UserActivity.select(fn.SUM(UserActivity.xp).alias("total"))
            .join(User)
            .where(User.user_id == str(user_id), User.guild == guild, UserActivity.mode == UserActivity.MODE_REDUCE)
        )

        total_added_xp = 0
        total_reduced_xp = 0
        if xp_added[0].total:
            total_added_xp = xp_added[0].total
        if xp_reduced[0].total:
            total_reduced_xp = xp_reduced[0].total

        if int(total_added_xp - total_reduced_xp) > 0:
            return total_added_xp - total_reduced_xp
        else:
            return 0
