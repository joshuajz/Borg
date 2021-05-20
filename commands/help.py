import discord
from methods.embed import create_embed, add_field
import asyncio


async def help_command(ctx, bot):
    """Help command"""

    def check(reaction, user):
        return user == ctx.author and str(reaction) in ["◀️", "▶️"]

    print("help command")
    pages = {}

    embed = create_embed("Help", "General commands that everyone can use.", "orange")
    add_field(embed, "!help or /help", "Provides this help command.", True)
    add_field(
        embed,
        "!commands or /command list",
        "Allows you to see all of the custom commands created for this server.",
        True,
    )
    add_field(
        embed,
        "/programs",
        "Allows you to edit your pgorams.\n/programs add\n/programs remove\n/programs edit",
        True,
    )
    add_field(
        embed,
        "!programs or /programs programs",
        "Allows you to see a user's programs list.",
        True,
    )

    pages[1] = embed

    embed2 = create_embed("Help", "Administrator Commands to Setup", "red")
    add_field(
        embed2,
        "/command",
        "Allows you to edit custom commands.\n/command add\n/command remove\n/command use",
        True,
    )
    add_field(
        embed2, "/programs setup", "Allows you to set the verification channel.", True
    )

    add_field(
        embed2,
        "/welcome",
        "Allows you to setup & toggle the welcome message.\n/welcome setup\n/welcome toggle",
        True,
    )

    pages[2] = embed2

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