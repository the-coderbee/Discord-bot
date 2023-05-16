import aiohttp
import discord

from guilds.models import Guild


class DiscordMessenger:
    @staticmethod
    async def send_message(message: str, guild_id: int):
        url = Guild.get_lvl_wh_url(guild_id)
        if not url:
            return
        async with aiohttp.ClientSession() as new_session:
            webhook = discord.Webhook.from_url(url, session=new_session)
            try:
                await webhook.send(message)
            except discord.NotFound:
                return
