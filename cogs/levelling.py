import discord
from discord import app_commands
from discord.ext import commands

from levelsystem.level_controller import XpType
from levelsystem.levelcard import LevelCard
from levelsystem.models import UserActivity
from settings import logging, BOT_COLOR
from users.models import User
from utils import checks

logger = logging.getLogger(__name__)


class Levelling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='leaderboard', description='Get Leaderboard of the server')
    @app_commands.describe(number='Number of users to show in leaderboard (maximum 20 allowed)')
    @checks.is_command_channel()
    async def show_leaderboard(self, ctx, number: int = 10):
        if number > 20:
            number = 20
        leaderboard = User.get_leaderboard(number, ctx.guild.id)
        emb = discord.Embed(title="Leaderboard", color=BOT_COLOR)
        emb.set_thumbnail(url=self.bot.user.avatar.url)
        output = "```"
        for user in leaderboard:
            member = await ctx.message.guild.fetch_member(user.user_id)
            output += f"{member.display_name:25} {user.total_xp} xp\n"
        output += "```"
        emb.add_field(name="Members", value=output, inline=False)
        await ctx.send(embed=emb)

    @commands.hybrid_command(name='level', description='Show level card of members')
    @checks.is_command_channel()
    async def level_card(self, ctx, member: discord.Member = None):
        try:
            member = member or ctx.message.author
        except AttributeError:
            return

        total_xp = UserActivity.get_total_xp(member.id, ctx.guild.id)
        if total_xp > 0:
            level_card = LevelCard(member, ctx.guild.id, total_xp)
            await level_card.save_user_avatar()
            level_card_path, required_xp = level_card.make_rank_card()
            file = discord.File(level_card_path, 'level-card.png')
            await ctx.send(file=file)
            await ctx.send(f'*```{required_xp} xp required for next level!```*')
            file.close()
            level_card.delete_image()
        else:
            if ctx.message.author.id == member.id:
                await ctx.send(f'*```You have 0 xp on this server```*')
            else:
                await ctx.send(f'{member.display_name} has 0 xp on this server')

    @commands.hybrid_command(name='give', description='Give xp to members')
    @app_commands.describe(xp_amount='The amount of xp you wish to give (maximum 1000 xp allowed per command)')
    @commands.has_permissions(administrator=True)
    @checks.is_command_channel()
    async def give_xp(self, ctx, member: discord.Member, xp_amount: float):
        if not 0 < xp_amount <= 1000:
            xp_amount = 1000
            await ctx.send(f'*```Xp reward should be between 0 to 1000```*')
        await ctx.send(f'{xp_amount} xp given to {member.mention}')
        await self.bot.levels.add_xp(ctx.message.id, member.id, ctx.guild.id, XpType.MANUAL, xp_amount)

    @commands.hybrid_command(name='rank', description='Show rank of a members')
    @checks.is_command_channel()
    async def get_rank(self, ctx, member: discord.Member = None):
        try:
            member = member or ctx.message.author
        except commands.BadArgument:
            return await ctx.send(f'{member} not found')
        rank = User.get_rank_from_leaderboard(member, ctx.guild.id)
        return await ctx.send(f'Hi {member.mention}! You are currently at rank {rank}')


async def setup(bot):
    await bot.add_cog(Levelling(bot))
