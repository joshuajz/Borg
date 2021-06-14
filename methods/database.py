import psycopg2
from dotenv import load_dotenv
import os


def get_credentials():
    cwd = os.getcwd().split("/")
    while cwd[-1] != "Borg":
        try:
            os.chdir("..")
        except:
            print(
                "Error moving directories.  Make sure you haven't renamed the folder that Borg resides in."
            )
            return

    load_dotenv()
    port = os.environ.get("database_port")
    if port is None or port == "" or port == " ":
        port = "5432"

    return os.environ.get("database_password"), port


def create_database():
    """Create the default postgresql database."""

    password, port = get_credentials()

    print("Creating Database.")

    # Connect to the default database
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

    # Create the Borg database
    try:
        cursor.execute("""CREATE database borg""")
    except:
        print("Database Already Created.")
        return database_connection()

    # Connect to the borg database
    con, cursor = database_connection()

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
        """CREATE TABLE courses (
            school text,
            code varchar(25),
            number smallint,
            department varchar(200),
            name text,
            description text,
            requirements text,
            academic_level text,
            units decimal,
            campus text
    )""",
    ]

    for command in commands:
        cursor.execute(command)

    return con, cursor


def database_connection() -> tuple:
    """Creates a connection to the Borg database."""

    password, port = get_credentials()

    # Connect
    con = psycopg2.connect(
        database="borg", user="postgres", password=password, host="localhost", port=port
    )

    # Turn auto automatic commits
    con.autocommit = True

    cursor = con.cursor()
    return (con, cursor)


class Guild_Info:
    """The Guild_Info class.  Provides all of the functions required for dealing with the Borg database."""

    def __init__(self, guild_id: int):
        """Initalizes self.guild_id & a database connection."""
        self.guild_id = guild_id

        # Grab a database connection
        self.db, self.cursor = database_connection()

    def grab_settings(self) -> dict:
        """Fetches the server's settings.

        Returns:
            dict or None: Returns None if there are no settings or the server's settings in a dictionary:
                {
                    'programs_channel': int, # The programs channel ID
                    'course_default_school': int # The default school for course selection for this server.
                }
        """

        grab_info = self.cursor.execute(
            "SELECT * FROM settings WHERE guild_id = %s", (self.guild_id,)
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

    def grab_welcome(self) -> dict:
        """Fetches a server's welcome settings.

        Returns:
            dict or None: Returns None if there are no settings or the welcome settings in a dictionary:
                {
                    'channel': int, # The channel ID where welcome messages are provided.
                    'message': str, # The message to welcome a user
                    'enabled': bool # Whether welcome messages are enabled.
                }
        """

        self.cursor.execute(
            "SELECT * FROM welcome WHERE user_id = %s", (self.guild_id,)
        )
        try:
            data_pull = self.cursor.fetchone()
            welcome = {
                "channel": data_pull[1],
                "message": data_pull[2],
                "enabled": data_pull[3],
            }
            return welcome
        except:
            return None

    def grab_commands(self) -> list:
        """Fetches all of the commands for the server.

        Returns:
            list or None: None if there are no commands otherwise a List of Tuples:
                (
                    command (str), # The name or denominator for the command
                    output (str), # The output message of the command
                    image (None or str) # A link to an image to embed in the command
                )
        """

        self.cursor.execute(
            "SELECT command, output, image FROM custom_commands WHERE guild_id = %s",
            (self.guild_id,),
        )
        try:
            return self.cursor.fetchall()
        except:
            return None

    def add_command(self, name: str, description: str, image=None):
        """Adds a command to the database.

        Args:
            name (str): The name or denominator for the command.
            description (str): The description or text displayed when the command is called.
            image (str, optional): A link to an image to embed. Defaults to None.
        """

        self.cursor.execute(
            "INSERT INTO custom_commands VALUES (%s, %s, %s, %s)",
            (self.guild_id, name, description, image),
        )

    def remove_command(self, command: str):
        """Removes a command from the database.

        Args:
            command (str): The name or denominator for the command.
        """

        self.cursor.execute(
            "DELETE FROM custom_commands WHERE guild_id = %s AND command = %s",
            (self.guild_id, command),
        )

    def grab_roles(self) -> list:
        """Provides all of the roles on a server.

        Returns:
            None or list: Provides None if there are no roles otherwise a List of Tuples:
                (
                    role_id (int), # The role's ID
                    command (str) # The denominator to call the command
                )
        """

        self.cursor.execute(
            "SELECT role_id, command FROM command_roles WHERE guild_id = %s",
            (self.guild_id,),
        )
        try:
            roles = self.cursor.fetchall()
            return roles
        except:
            return None

    def grab_role(self, command=None, role_id=None) -> tuple:
        """Fetches a specific role.

        Args:
            command (str, optional): The command to call the role. Defaults to None.
            role_id (int, optional): The role's actual ID. Defaults to None.

        Returns:
            None or Tuple: Provides None if there isn't a role otherwise a Tuple:
                (
                    guild_id (int), # The guild's ID
                    role_id (int), # The ID of the role to add
                    command (str) # The command that will toggle that role
                )
        """
        if command:
            self.cursor.execute(
                "SELECT * FROM command_roles WHERE guild_id = %s AND command = %s",
                (self.guild_id, command),
            )
            try:
                return self.cursor.fetchone()
            except:
                return None
        elif role_id:
            self.cursor.execute(
                "SELECT * FROM command_roles WHERE guild_id = %s AND role_id = %s",
                (self.guild_id, role_id),
            )
            try:
                return self.cursor.fetchone()
            except:
                return None

    def check_role(self, role_id, command) -> bool:
        """Checks to see if a role exists when adding a new role to the database.

        Args:
            role_id (int): The actual role's ID
            command (str): The command to call the role

        Returns:
            bool or None: Will return True if these values exist in the database, otherwise will return False.
        """

        self.cursor.execute(
            "SELECT EXISTS(SELECT * FROM command_roles WHERE guild_id = %s AND (role_id = %s OR command = %s))",
            (self.guild_id, role_id, command),
        )
        try:
            return self.cursor.fetchone()
        except:
            return False

    def add_role(self, role_id, command):
        """Adds a role to the database

        Args:
            role_id (int): The actual role's id
            command (str): The command to call the role
        """

        self.cursor.execute(
            "INSERT INTO command_roles VALUES (%s, %s, %s)",
            (self.guild_id, role_id, command),
        )

    def remove_role(self, role_id):
        """Removes a role from the database

        Args:
            role_id (int): The role's ID
        """

        self.cursor.execute(
            "DELETE FROM command_roles WHERE guild_id = %s AND role_id = %s",
            (self.guild_id, role_id),
        )

    def grab_programs(self, user_id: int) -> str:
        """Grabs all of a user's programs

        Args:
            user_id (int): The user's ID

        Returns:
            str or None: None if the user has no programs.  A string containing all of the programs.  \n Seperated
        """

        self.cursor.execute(
            "SELECT description FROM programs WHERE guild_id = %s AND user_id = %s",
            (self.guild_id, user_id),
        )
        try:
            return (self.cursor.fetchone())[0]
        except:
            return None

    def create_default_settings(self):
        """Creates the default settings value for a guild."""

        self.cursor.execute(
            "INSERT INTO settings(guild_id, programs_channel, courses_default_school) VALUES (%s, %s, %s)",
            (self.guild_id, None, None),
        )
