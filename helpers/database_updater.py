import sqlite3
import os
import sys
import asyncio

sys.path.append("../")
from methods.database import database_connection
from methods.database import SERVERS_DIR


async def main():
    commands = []

    os.chdir(SERVERS_DIR)
    list_dir = os.listdir()
    for f in list_dir:

        db = await database_connection(f)

        for command in commands:
            db["db"].execute(command)
            db["con"].commit()


asyncio.run(main())