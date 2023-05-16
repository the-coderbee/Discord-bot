import discord
from discord.ext import commands

from settings import STATIC_IMG_DIR


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        welcome_msg = f'Hey {member.display_name}! Welcome to **{member.guild.name}**'
        embed = discord.Embed(title='', color=discord.Color.from_rgb(252, 186, 3))
        file = discord.File(STATIC_IMG_DIR / 'welcome.gif', filename='welcome.gif')
        embed.set_image(url=f'attachment://welcome.gif')
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name=welcome_msg, value='', inline=False)
        embed.add_field(name='', value='It\'s nice to see you.')
        embed.set_author(name=f'{member.guild.owner.display_name}')
        embed.set_footer(text="Let's Play!")
        await channel.send(file=file, embed=embed)

        # user dm embed
        dm_msg = f'Hello {member.display_name}! You just joined {member.guild.name}.\n'
        emb = discord.Embed(title="", color=discord.Color.from_rgb(252, 186, 3))
        file1 = discord.File(STATIC_IMG_DIR / 'primeguardian.gif', filename='primeguardian.gif')
        emb.set_thumbnail(url=f'attachment://primeguardian.gif')
        emb.set_author(name=f'{self.bot.user.name}')
        emb.add_field(name=dm_msg, value='', inline=False)
        emb.add_field(name=f'Please check these out:', value=f'1. #Rules', inline=False)
        emb.set_footer(text='You are good to go after you have completed few initial tasks.')
        try:
            await member.send(file=file1, embed=emb)
        except discord.HTTPException:
            return


async def setup(bot):
    welcome_bot = Welcome(bot)
    await bot.add_cog(welcome_bot)
