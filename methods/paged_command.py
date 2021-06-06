import discord
import asyncio
from methods.embed import create_embed, add_field


async def page_command(ctx, bot, items: list, title: str):
    """Creates a paged dialog for printing out large quantities of items

    Args:
        ctx (discord.Context): Context for the command call
        bot (discord.Bot): The actual bot instance
        items (list): A list of items to display
        title (str): Title of the page list
    """

    def check(reaction: discord.Reaction, user: discord.User) -> bool:
        """Checks to see if the user who added the reaction is the same as the person who callled the command

        Args:
            reaction (discord.Reaction): The actual added reaction
            user (discord.User): The user instance

        Returns:
            bool: If the user who ran the command added the reaction
        """

        return user == ctx.author and str(reaction) in ["◀️", "▶️"]

    # Sort the items list
    items.sort()

    # Creates lists splitting every 20 values
    pages_lists = []
    for i in range(0, len(items), 20):
        pages_lists.append(items[i : i + 20])

    # If there is only one list, we can just print out the first page and then end
    if len(pages_lists) == 1:
        l1, l2 = pages_lists[0][0:10], pages_lists[0][10::]
        embed = create_embed(title, "", "orange")
        add_field(embed, "List 1:", "\n".join(l1), True)
        if l2:
            add_field(embed, "List 2:", "\n".join(l2), True)
        await ctx.send(embed=embed)
        return

    # Creates the different embeds for each of the pages in a dictionary
    # ie. messages[1], messages[2]... will be embeds
    messages = {}
    i = 1
    for m in pages_lists:
        embed = create_embed(title, "", "orange")
        add_field(embed, "List 1:", "\n".join(m[0:10]), True)
        if m[10::]:
            add_field(embed, "List 2:", "\n".join(m[10::]), True)
        messages[i] = embed
        i += 1

    # Send the original message w/ reactions
    msg = await ctx.send(embed=messages[1])
    await msg.add_reaction("◀️")
    await msg.add_reaction("▶️")

    # Current page & total amount of pages
    current_page = 1
    amount_pages = len(messages)

    while True:
        try:
            # Waiting for a reaction to be added
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=60 * 2.5, check=check
            )

            # Move to the next page if we're not at the end
            if current_page != amount_pages and str(reaction) == "▶️":
                current_page += 1
                await msg.edit(embed=messages[current_page])
                await msg.remove_reaction(reaction, user)

            # Move back a page if we're not at the start
            elif current_page != 1 and str(reaction) == "◀️":
                current_page -= 1
                await msg.edit(embed=messages[current_page])
                await msg.remove_reaction(reaction, user)
            # Invalid movement, remove the reaction
            else:
                await msg.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            # Timeout over
            await msg.delete()
            break