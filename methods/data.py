from typing import Union


def parse_id(data: str) -> int:
    """Finds a user given some sort of user data -> userid (178543252637483009) user @ (<@178543252637483009>) or (<@!178543252637483009>)

    Args:
        data (str): User data

    Returns:
        int: User ID
    """

    if type(data) == int:
        return data

    try:
        data = data.strip()
    except:
        return False

    if data.isnumeric() and len(data) == 18:
        # User ID is given
        user_id = int(data)
    elif data[0:3] == "<@!" or data[0:3] == "<@&":
        user_id = int(data[3:-1])
    elif data[0:2] == "<@" or data[0:2] == "<#":
        user_id = int(data[2:-1])
    else:
        return False

    return user_id


def parse_channel(data: str) -> int:
    """Finds a channel given some sort of data ie. <#839744778517872650> -> 839744778517872650

    Args:
        data (str): The channel data

    Returns:
        int: The channel ID
    """

    if type(data) == int:
        return data

    try:
        data = data.strip()
    except:
        return False

    if data.isnumeric() and len(data) == 18:
        user_id = int(data)
    elif data[0:2] == "<#":
        user_id = int(data[2:-1])
    else:
        return False

    return user_id


def find_channel(ctx, channel: str) -> Union[int, list]:
    """Finds a channel given it's name

    Args:
        ctx (discord.Context): Discord.py's Context
        channel (str): The name of the channel

    Returns:
        Union[int, list]: Either an int with the channel ID or an error message
    """

    channel_id = [i.id for i in ctx.guild.channels if i.name == channel]

    if len(channel_id) == 1:
        return int(channel_id[0])
    else:
        return ["False", "There are multiple channels with that name."]
