import psycopg2
from dotenv import load_dotenv
import os


def create_database(password: str, port="5432"):
    # Connect to the default postgres DB

    print("Creating Database.")

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

    try:
        cursor.execute("""CREATE database borg""")
    except:
        print("Database Already Created.")
        return database_connection(password, port)

    # Connect to the borg database
    con, cursor = database_connection(password, port)

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
        cursor.execute(command)

    return con, cursor


def database_connection(password: str, port="5432"):
    con = psycopg2.connect(
        database="borg", user="postgres", password=password, host="localhost", port=port
    )
    con.autocommit = True
    cursor = con.cursor()
    return (con, cursor)


class Guild_Info:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        load_dotenv()
        port = os.environ.get("database_port")
        if port:
            result = database_connection(
                os.environ.get("database_password"),
                port=os.environ.get("database_port"),
            )
        else:
            result = database_connection(os.environ.get("database_password"))
        self.db, self.cursor = result

    def grab_settings(self):
        grab_info = self.cursor.execute(
            "SELECT * FROM settings WHERE user_id = %s", (self.guild_id,)
        )
        try:
            grab_info = self.cursor.fetchone()
            settings = {
                "programs_channel": grab_info[1],
                "course_default_school": grab_info[2],
            }
            return settings
        except:
            return None

    def grab_welcome(self):
        grab_info = self.cursor.execute(
            "SELECT * FROM welcome WHERE user_id = %s", (self.guild_id,)
        ).fetchone()
        welcome = {
            "channel": grab_info[1],
            "message": grab_info[2],
            "enabled": grab_info[3],
        }
        return welcome

    def grab_commands(self):
        self.cursor.execute(
            "SELECT command, output, image FROM custom_commands WHERE guild_id = %s",
            (self.guild_id,),
        )
        try:
            return self.cursor.fetchall()
        except:
            return None

    def add_command(self, name, description, image=None):
        self.cursor.execute(
            "INSERT INTO custom_commands VALUES (%s, %s, %s, %s)",
            (self.guild_id, name, description, image),
        )

    def remove_command(self, command):
        self.cursor.execute(
            "DELETE FROM custom_commands WHERE guild_id = %s AND command = %s",
            (self.guild.id, command),
        )

    def grab_roles(self):
        grab_roles = self.cursor.execute(
            "SELECT role_id, command FROM command_roles WHERE guild_id = %s",
            (self.guild_id,),
        ).fetchall()
        return grab_roles

    def grab_programs(self, user_id: int):
        grab_programs = self.cursor.execute(
            "SELECT description FROM programs WHERE guild_id = %s AND user_id = %s",
            (self.guild_id, user_id),
        ).fetchone()
        return grab_programs
