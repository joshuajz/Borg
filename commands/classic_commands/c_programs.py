from discord.ext import commands
import sys
import re

sys.path.append("../..")
from commands.programs import (
    programs,
    programs_add,
    programs_remove,
    programs_edit,
    programs_setup,
)
from methods.data import parse_id
from methods.embed import create_embed, create_embed_template


class ClassicPrograms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="programs")
    async def _programs(self, ctx):
        """!programs command"""
        content = ctx.message.content.split(" ")
        if len(content) == 1:
            embed = create_embed(
                "Command: !programs",
                "**Description**: Allows you to interact with programs commands.\n**Sub Commands**:\n!programs {user} - Allows you to see a user's programs. (ex: !programs <@749359897405161522>)\n!programs add - Allows you to add programs to your list.\n!programs remove - Allows you to remove programs from your list.\n!programs edit - Allows you to edit one of your programs.\n!commands setup - Allows an admin to setup a programs confirmation channel.",
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
                user = parse_id(user.group())
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
                return

            content = content[2::]

            user, content = grab_user(content)
            if user is None:
                user = ctx.author.id

            result = await programs_remove(ctx, " ".join(content), user)
            await ctx.send(embed=result[1])

        elif subcommand == "edit" or subcommand == "e":
            #: !command edit 1 New Program
            if len(content) < 4:
                embed = create_embed(
                    "Command: !programs edit",
                    "**Description**: Allows you to edit a program in your list.  Provide the number for the program, and the new text.\n**Usage**:\n!programs edit 1 Queens CS\n!programs edit 1 Queens CS <@749359897405161522>",
                    "orange",
                )
                await ctx.send(embed=embed)
                return

            content = content[2::]

            user, content = grab_user(content)
            if user is None:
                user = ctx.author.id
            before = content[0]
            after = " ".join(content[1::])

            result = await programs_edit(ctx, self.bot, user, before, after)
            await ctx.send(embed=result[1])

        elif subcommand == "setup" or subcommand == "s":
            #: !command setup <#846962522065993768>
            if len(content) == 2 or len(content) > 3:
                embed = create_embed(
                    "Command: !programs setup",
                    "**Description**: Allows an administrator to setup a programs verification channel.\n**Usage**:\n!programs setup <@799848795050606607>",
                    "orange",
                )
                await ctx.send(embed=embed)
                return

            channel_id = parse_id(content[2])
            if not channel_id:
                embed = create_embed_template("Invalid Setup Channel", "", "error")
                await ctx.send(embed=embed)
                return

            result = await programs_setup(ctx, channel_id)
            await ctx.send(embed=result[1])
        else:
            attempt_user = parse_id(subcommand)
            if attempt_user:
                user_id = attempt_user
            else:
                user_id = ctx.guild.get_member_named(subcommand).id

            p = await programs(ctx, self.bot, user_id)

            await ctx.send(embed=p[1])


def setup(bot):
    bot.add_cog(ClassicPrograms(bot))
