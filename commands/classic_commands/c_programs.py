import discord
from discord.ext import commands
import sys

sys.path.append("../..")
from commands.programs import programs
from methods.data import parse_user
from methods.embed import create_embed


class Classic_Programs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="programs")
    async def _programs(self, ctx):
        content = ctx.message.content.split(" ")
        if len(content) != 2:
            embed = create_embed(
                "Command: !programs",
                "**Description**: Allows you to see a user's programs.\n**Usage**:\n!programs Borg\n!programs <@749359897405161522>",
                "orange",
            )
            await ctx.send(embed=embed)
            return

        user = content[1]

        user_id = parse_user(user)
        if not user_id:
            user_id = ctx.guild.get_member_named(content[1]).id
        if user_id == False:
            user_id = user.id

        p = await programs(ctx, user_id)

        await ctx.send(embed=p[1])


def setup(bot):
    bot.add_cog(Classic_Programs(bot))