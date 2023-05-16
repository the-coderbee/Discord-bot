import discord

from classes.controllers import BaseController
from levelsystem.models import UserActivity, XpType
from users.models import User


class Levels(BaseController):

    async def add_xp(self, message_id: int, user_id: int, guild_id: int, xp_type: XpType, manual_xp: float = 0):
        await self._save_xp_to_db(message_id, user_id, guild_id, xp_type, manual_xp)

    async def reduce_xp(self, message_id: int, user_id: int, guild_id: int, xp_type: XpType, mode):
        await self._save_xp_to_db(message_id, user_id, guild_id, xp_type, mode)

    async def _get_xp_modifier(self, user_id: int, guild_id: int):
        modifier = 1.0
        member = await self.bot_handler.fetch_member(user_id, guild_id)
        special_role = await self.bot_handler.fetch_role('special', guild_id)
        if special_role in member.roles:
            modifier = 1.5
        return modifier

    async def _save_xp_to_db(self, message_id: int, user_id: int, guild_id: int,
                             xp_type: XpType, manual_xp: float = 0, mode=UserActivity.MODE_ADD):
        user, guild = User.fetch_user_and_guild_by_id(user_id, guild_id)
        user_activity = UserActivity(message_id=message_id, user=user, guild_id=guild.guild_id)
        modifier = await self._get_xp_modifier(user_id, guild.guild_id)
        (changed, current_lvl, new_lvl) = user_activity.save_new_recorded_xp(xp_type, mode, manual_xp, modifier)
        if changed:
            member = await self.bot_handler.fetch_member(user_id, guild.guild_id)
            for i in range(new_lvl - current_lvl):
                message = f'{member.mention} has reached level {new_lvl}'
                await self.announcement(message, guild.guild_id)

    async def process_message(self, message: discord.Message):
        await self.add_xp(message.id, message.author.id, message.guild.id, XpType.MESSAGE)

    async def process_reaction(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == 'REACTION_ADD':
            await self.add_xp(payload.message_id, payload.user_id, payload.guild_id, XpType.REACTION)
        else:
            await self.reduce_xp(payload.message_id, payload.user_id, payload.guild_id, XpType.REACTION,
                                 UserActivity.MODE_REDUCE)

    async def announcement(self, message: str, guild_id: int):
        await self.messenger.send_message(message, guild_id)
