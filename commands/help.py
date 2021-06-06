import discord
from methods.embed import create_embed, add_field
import asyncio


async def help_command(ctx: discord.Context, bot: discord.Bot):
    """Help Command

    Args:
        ctx (discord.Context): Context
        bot (discord.Bot): Bot instance
    """

    def check(reaction, user):
        return user == ctx.author and str(reaction) in ["◀️", "▶️"]

    pages = {}

    embed = create_embed(
        "Help: Table of Contents",
        "Page `1/4`\nPage 1: Table of Contents\nPage 2: General Commands\nPage 3: University Commands\nPage 4: Setup Commands",
        "orange",
    )
    pages[1] = embed

    embed = create_embed("Help: General Commands", "Page `2/4`", "orange")
    add_field(
        embed,
        "Commands",
        "Allow you to use this server's custom commands.\n!commands - Lists the commands.",
        False,
    )
    pages[2] = embed

    embed = create_embed("Help: University Commands", "Page `3/4`", "orange")
    add_field(
        embed,
        "Programs",
        "Allows you to interact with programs lists.\n!programs - Allows you to see a user's programs.\n/programs add - Add programs.\n/programs remove - Remove programs.\n/programs edit - Edit one of your programs.\n",
        False,
    )
    add_field(
        embed,
        "Courses",
        "Allows you to lookup a University's course.\n/course - Lookup a course.",
        False,
    )
    pages[3] = embed

    embed = create_embed("Help: Setup Commands", "Page `4/4`", "orange")
    add_field(
        embed,
        "Programs",
        "Allows you to setup the channel for programs verification.\n/programs setup {channel}\n",
        False,
    )
    add_field(
        embed,
        "Commands",
        "Allows you to add and remove your server's custom commands.\n/command add - Adds a command.\n/command remove - Removes a command.",
        False,
    )
    pages[4] = embed

    # Send the original message w/ reactions
    msg = await ctx.send(embed=pages[1])
    await msg.add_reaction("◀️")
    await msg.add_reaction("▶️")

    # Current page & total amount of pages
    current_page = 1
    amount_pages = len(pages)

    while True:
        try:
            # Waiting for a reaction to be added
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=60 * 2.5, check=check
            )

            # Move to the next page if we're not at the end
            if current_page != amount_pages and str(reaction) == "▶️":
                current_page += 1
                await msg.edit(embed=pages[current_page])
                await msg.remove_reaction(reaction, user)

            # Move back a page if we're not at the start
            elif current_page != 1 and str(reaction) == "◀️":
                current_page -= 1
                await msg.edit(embed=pages[current_page])
                await msg.remove_reaction(reaction, user)
            # Invalid movement, remove the reaction
            else:
                await msg.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            # Timeout over
            await msg.delete()
            break