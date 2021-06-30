from methods.database import database_connection, welcome_grab, welcome_update
from methods.embed import create_embed, add_field


async def welcome_handling(ctx, client):
    """Handles welcoming new users."""
    db = await database_connection()

    # Grabs this server's info
    welcome_info = await welcome_grab(ctx.guild.id, db)

    # Returns if there isn't any
    if len(welcome_info) != 3:
        return

    message = welcome_info["message"]
    channel = welcome_info["channel"]
    enabled = welcome_info["enabled"]

    if message is None or channel is None or enabled is False:
        return

    # Send the message
    channel = client.get_channel(int(channel))
    await channel.send(message.replace("{{USER}}", ctx.mention))


async def welcome_setup(ctx, channel: int, description: str):
    """Sets up the welcome messages."""
    if ctx.author.guild_permissions.administrator is False:
        return

    db = await database_connection()

    # Updates the DB
    await welcome_update(
        ctx.guild.id, {"channel": channel, "message": description, "enabled": True}, db
    )

    # Send status message
    embed = create_embed("Welcome Message Created Successfully", "", "light_green")
    add_field(embed, "Message", description, True)
    add_field(embed, "Channel", channel, True)
    await ctx.channel.send(embed=embed, hidden=True)


async def welcome_toggle(ctx):
    if ctx.author.guild_permissions.administrator is False:
        return

    db = await database_connection()

    welcome_info = await welcome_grab(ctx.guild.id, db)

    if welcome_info["enabled"] is False:
        embed = create_embed("Welcome Message Enabled", "", "light_green")
        welcome_info["enabled"] = True
    else:
        embed = create_embed("Welcome Message Disabled", "", "red")
        welcome_info["enabled"] = False

    await welcome_update(ctx.guild.id, welcome_info, db)

    await ctx.channel.send(embed=embed, hidden=True)
