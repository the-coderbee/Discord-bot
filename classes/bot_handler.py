from discord.ext import commands


class BotHandler:
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    async def fetch_guild(self, guild_id: int):
        return await self.bot.fetch_guild(guild_id)

    async def fetch_member(self, member_id: int, guild_id: int):
        guild = await self.fetch_guild(guild_id)
        return await guild.fetch_member(member_id)

    async def fetch_role(self, role_name: str, guild_id: int):
        guild = await self.fetch_guild(guild_id)
        roles = await guild.fetch_roles()
        for role in roles:
            if role.name == role_name:
                return role
        return None
