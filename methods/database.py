import sqlite3
import os
from shutil import copyfile
import discord
from typing import Dict

SERVERS_DIR = f"{os.getcwd()}/servers"
DEFAULT_DIR = os.getcwd()


async def check_filesystem(client: discord.Client):
    """Creates the filesystem"""

    # Check to see if there is a "servers" directory
    if os.path.isdir("servers") == False:
        os.makedirs("servers")

    # Open the "servers" directory
    os.chdir(SERVERS_DIR)

    # List of directory
    list_dir = os.listdir()

    for guild in [i for i in client.guilds if str(i.id) not in list_dir]:
        # Create a folder
        os.mkdir(str(guild.id))

    # Checks every guild
    for guild in os.listdir():
        # List of files in the directory
        l_dir = os.listdir(guild)

        # Creates a database file if there isn't one
        if "database.db" not in l_dir:
            db_conn = sqlite3.connect(f"{SERVERS_DIR}/{guild}/database.db")
            db = db_conn.cursor()

            await create_database({"db": db, "con": db_conn})


async def create_database(db: dict) -> bool:
    db_commands = [
        "CREATE TABLE reaction_roles ([role_id] int, [message_id] int, [reaction_id] int, [channel_id] int)",
        "CREATE TABLE normal_roles (role_id int, command text)",
        "CREATE TABLE custom_commands (command text, output text, image text)",
        "CREATE TABLE programs (user_id int, description text)",
        "CREATE TABLE welcome (channel int, message text, enabled bool)",
        """CREATE TABLE "infractions" (
        "id"	INTEGER NOT NULL DEFAULT 0 PRIMARY KEY AUTOINCREMENT,
        "datetime"	TEXT,
        "length"	TEXT,
        "type"	TEXT,
        "user_id"	INTEGER,
        "moderator_id"	INTEGER,
        "reason"	TEXT,
        "active"    BOOL)""",
        "CREATE TABLE settings (programs_channel text)",
    ]

    for command in db_commands:
        db["db"].execute(command)

    db["db"].execute(
        "INSERT INTO welcome VALUES (?, ?, ?)",
        (
            None,
            None,
            False,
        ),
    )
    db["db"].execute("INSERT INTO settings VALUES (?)", (None,))

    db["con"].commit()

    return True


async def database_connection(
    guild: int,
) -> dict:
    """Creates a database connection with a guild id"""

    db_connection = sqlite3.connect(f"{SERVERS_DIR}/{guild}/database.db")
    db = db_connection.cursor()

    return {"con": db_connection, "db": db}


async def create_filesystem(ctx):
    """Creates a filesystem for the new server."""

    guild = ctx.id

    # Open the "servers" directory
    os.chdir(SERVERS_DIR)

    # List of directory
    list_dir = os.listdir()

    if str(guild) not in list_dir:
        os.mkdir(str(guild))

    # Creates a database file
    db_conn = sqlite3.connect(f"{SERVERS_DIR}/{guild}/database.db")
    db = db_conn.cursor()

    await create_database({"db": db, "con": db_conn})
