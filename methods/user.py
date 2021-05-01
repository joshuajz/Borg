import discord


def find_user(data: str) -> int:
    """Finds a user given some sort of user data -> userid (178543252637483009) user @ (<@178543252637483009> OR <@!178543252637483009>)"""

    data = data.strip()
    if data.isnumeric() and len(data) == 18:
        # User ID is given
        user_id = int(data)
    elif data[0:3] == "<@!":
        user_id = int(data[3:-1])
    elif data[0:2] == "<@":
        user_id = int(data[2:-1])
    else:
        return False

    return user_id
