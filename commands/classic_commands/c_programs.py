import discord
from discord.ext import commands
import sys
import re

sys.path.append("../..")
from commands.programs import programs, programs_add, programs_remove
from methods.data import parse_user
from methods.embed import create_embed


class Classic_Programs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="programs")
    async def _programs(self, ctx):
        content = ctx.message.content.split(" ")
        if len(content) == 1:
            embed = create_embed(
                "Command: !programs",
                "**Description**: Allows you to interact with programs commands.\n**Sub Commands**:\n!programs {user} - Allows you to see a user's programs. (ex: !programs <@749359897405161522>)\n!programs add - Allows you to add programs to your list.\n!programs remove - Allows you to remove programs from your list.\n!programs edit - Allows you to edit one of your programs.",
                "orange",
            )
            await ctx.send(embed=embed)
            return

        subcommand = content[1]

        def grab_user(content):
            user = re.search(r"<@(?:&|!|)[0-9]{18}>", " ".join(content))
            if not user:
                return None, content
            else:
                content = " ".join(content).replace(user, "").split(" ")
                user = parse_user(user.group())
                return user, content

        if subcommand == "add" or subcommand == "a":

            #: !programs add Queens CS
            if len(content) == 2:
                embed = create_embed(
                    "Command: !programs add",
                    "**Description**: Allows you to add programs to your list.\n**Usage**:\n!programs add Queens CS, Mcgill CS, UW CS\n!programs add Queens CS, UW CS <@749359897405161522>",
                    "orange",
                )
                await ctx.send(embed=embed)
            else:
                content = content[2::]

                user, content = grab_user(content)
                if user is None:
                    user = ctx.author.id

                potential_programs = " ".join(content).split("\n")
                if len(potential_programs) == 1:
                    potential_programs = [
                        i.strip() for i in potential_programs[0].split(",")
                    ]
                else:
                    p = []
                    for i in potential_programs:
                        additions = [g.strip() for g in i.split(",")]
                        p.extend(additions)
                    potential_programs = p

                result = await programs_add(ctx, self.bot, potential_programs, user)
                await ctx.send(embed=result[1])

        elif subcommand == "remove" or subcommand == "r":
            if len(content) == 2:
                embed = create_embed(
                    "Command: !programs remove",
                    "**Description**: Allows you to remove programs from your list.  Provide a comma seperated list of numbers, or * to remove all of your programs.\n**Usage**:\n!programs remove 1, 2, 3\n!programs remove * <@749359897405161522>",
                    "orange",
                )
                await ctx.send(embed=embed)

            content = content[2::]

            user, content = grab_user(content)
            if user is None:
                user = ctx.author.id

            result = await programs_remove(ctx, " ".join(content), user)
            await ctx.send(embed=result[1])

        attempt_user = parse_user(subcommand)
        if attempt_user:
            user = content[1]

            user_id = parse_user(user)
            if not user_id:
                user_id = ctx.guild.get_member_named(user).id

            p = await programs(ctx, self.bot, user_id)

            await ctx.send(embed=p[1])


def setup(bot):
    bot.add_cog(Classic_Programs(bot))