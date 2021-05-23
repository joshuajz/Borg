import sqlite3
import os
import sys

sys.path.append("../")
from methods.database import database_connection, SERVERS_DIR


os.chdir(SERVERS_DIR)

target_database = f"{SERVERS_DIR}/target.db"

list_dir = os.listdir()
for f in list_dir:
    db = database_connection(f)

    tables = (
        db["db"].execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    )
    print(tables)
    print("\n\n")
