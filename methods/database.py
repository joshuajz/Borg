import psycopg2
from dotenv import load_dotenv
import os


def create_database(password: str, port="5432"):
    # Connect to the default postgres DB
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password=password,
        host="localhost",
        port=port,
    )

    # Auto commit changes
    con.autocommit = True

    # Create Borg's database
    cursor = con.cursor()
    cursor.execute("""CREATE database borg""")

    # Connect to the borg database
    con = psycopg2.connect(
        database="borg",
        user="postgres",
        password=password,
        host="localhost",
        port=port,
    )

    cursor = con.cursor()

    # Auto commit changes
    con.autocommit = True

    # Create the tables
    commands = [
        """CREATE TABLE custom_commands (
        guild_id bigint,
        command text,
        output text,
        image text
    )""",
        """CREATE TABLE command_roles (
        guild_id bigint,
        role_id bigint,
        command text
    )""",
        """CREATE TABLE programs (
        guild_id bigint,
        user_id bigint,
        description text
    )""",
        """CREATE TABLE settings (
        guild_id bigint,
        programs_channel bigint,
        courses_default_school varchar(255)
    )
    """,
        """CREATE TABLE welcome (
        guild_id bigint,
        channel bigint,
        message text,
        enabled boolean
    )""",
    ]

    for command in commands:
        print(command)
        cursor.execute(command)

    con.close()