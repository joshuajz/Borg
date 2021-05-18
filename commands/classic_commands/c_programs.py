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
    async def _programs(self, ctx, user: discord.User):
        user_id = parse_user(user)
        if user_id == False:
            user_id = user.id

        p = await programs(ctx, user_id)

        # Successfully grabbed programs
        if p[0] == True:
            user = self.bot.get_user(user_id)
            embed = create_embed(
                f"{user.name}#{user.discriminator}'s Programs", p[1], "orange"
            )
            await ctx.send(embed=embed)
        else:
            # Return the error
            await ctx.send(p[1])


def setup(bot):
    bot.add_cog(Classic_Programs(bot))