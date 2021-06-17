import asyncpg
from dotenv import load_dotenv
import os
import asyncio
from asyncinit import asyncinit


async def get_credentials():
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
        port = None

    return os.environ.get("database_password"), port


async def create_database():
    """Create the default postgresql database."""

    password, port = await get_credentials()

    print("Creating Database.")

    # Connect to the default database
    con = await asyncpg.connect(
        database="postgres",
        user="postgres",
        password=password,
        host="localhost",
        port=port,
    )

    # Create the Borg database
    try:
        con.cursor("""CREATE database borg""")
    except:
        print("Database Already Created.")
        return await database_connection()

    # Connect to the borg database
    con = await database_connection()

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
        async with con.transaction():
            try:
                await con.execute(command)
            except asyncpg.exceptions.DuplicateTableError as e:
                print(e)

    return con


async def database_connection():
    """Creates a connection to the Borg database."""

    password, port = await get_credentials()

    # Connect
    con = await asyncpg.connect(
        database="borg",
        user="postgres",
        password=password,
        host="localhost",
        port=int(port),
    )

    return con


@asyncinit
class Programs_DB:
    async def __init__(self, guild_id: int):
        """Initalizes self.guild_id & a database connection."""
        self.guild_id = guild_id

        # Grab a database connection
        self.db = await database_connection()

    async def grab_programs(self, user_id: int) -> str:
        """Grabs all of a user's programs

        Args:
            user_id (int): The user's ID

        Returns:
            str or None: None if the user has no programs.  A string containing all of the programs.  \n Seperated
        """

        programs_response = await self.db.fetchrow(
            "SELECT description FROM programs WHERE guild_id = $1 AND user_id = $2",
            self.guild_id,
            user_id,
        )

        try:
            return programs_response[0]
        except:
            return None

    async def update_programs(self, user_id, new_programs):
        await self.db.execute(
            "UPDATE programs SET description = $1 WHERE guild_id = $2 AND user_id = $3",
            new_programs,
            self.guild_id,
            user_id,
        )

    async def check_programs_exists(self, user_id):
        count = await self.db.fetchrow(
            "SELECT COUNT(user_id) FROM programs WHERE guild_id = $1 AND user_id = $2",
            self.guild_id,
            user_id,
        )

        return count[0]

    async def add_programs(self, user_id, programs):
        await self.db.execute(
            "INSERT INTO programs VALUES ($1, $2, $3)", self.guild_id, user_id, programs
        )


@asyncinit
class Roles_DB:
    async def __init__(self, guild_id: int):
        """Initalizes self.guild_id & a database connection."""
        self.guild_id = guild_id

        # Grab a database connection
        self.db = await database_connection()

    async def grab_roles(self) -> list:
        """Provides all of the roles on a server.

        Returns:
            None or list: Provides None if there are no roles otherwise a List of Tuples:
                (
                    role_id (int), # The role's ID
                    command (str) # The denominator to call the command
                )
        """

        roles = await self.db.fetch(
            "SELECT role_id, command FROM command_roles WHERE guild_id = $1",
            self.guild_id,
        )

        try:
            return roles
        except:
            return None

    async def grab_role(self, command=None, role_id=None) -> tuple:
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
            command_response = await self.db.fetchrow(
                "SELECT * FROM command_roles WHERE guild_id = $1 AND command = $2",
                self.guild_id,
                command,
            )

            return command_response

        elif role_id:

            command_response = await self.db.fetchrow(
                "SELECT * FROM command_roles WHERE guild_id = $1 AND role_id = $2",
                self.guild_id,
                role_id,
            )

            return command_response

    async def check_role(self, role_id: int, command: str) -> bool:
        """Checks to see if a role exists when adding a new role to the database.

        Args:
            role_id (int): The actual role's ID
            command (str): The command to call the role

        Returns:
            bool or None: Will return True if these values exist in the database, otherwise will return False.
        """

        role_response = await self.db.fetchrow(
            "SELECT EXISTS(SELECT * FROM command_roles WHERE guild_id = $1 AND (role_id = $2 OR command = $3))",
            self.guild_id,
            role_id,
            command,
        )

        return not (role_response["exists"])

    async def add_role(self, role_id, command):
        """Adds a role to the database

        Args:
            role_id (int): The actual role's id
            command (str): The command to call the role
        """

        async with self.db.transaction():
            try:
                await self.db.execute(
                    "INSERT INTO command_roles VALUES ($1, $2, $3)",
                    self.guild_id,
                    role_id,
                    command,
                )

            except Exception as e:
                print(e)

    async def remove_role(self, role_id):
        """Removes a role from the database

        Args:
            role_id (int): The role's ID
        """

        async with self.db.transaction():
            try:
                await self.db.execute(
                    "DELETE FROM command_roles WHERE guild_id = $1 AND role_id = $2",
                    self.guild_id,
                    role_id,
                )

            except Exception as e:
                print(e)


@asyncinit
class Courses_DB:
    async def __init__(self, school):
        """Initalizes self.guild_id & a database connection."""
        self.school = school

        # Grab a database connection
        self.db = await database_connection()

        self.SCHOOLS = ("queens", "uoft", "waterloo")

    async def fetch_school(self, department):
        return await self.db.fetch(
            "SELECT school FROM courses WHERE department = $1", department
        )

    async def fetch_codes_from_department(self, department):
        result = await self.db.fetch(
            "SELECT code, name FROM courses WHERE school = $1 AND department = $2",
            self.school,
            department.strip().upper(),
        )
        return result

    async def fetch_course(self, course):
        result = await self.db.fetch(
            "SELECT * FROM courses WHERE school = $1 AND code = $2", self.school, course
        )
        return result

    async def department_exist(self, department):
        result = await self.db.fetchrow(
            "SELECT EXISTS(SELECT department FROM courses WHERE school = $1 AND department = $2)",
            self.school,
            department,
        )
        return result[0]

    async def fetch_schools_with_department(self, department):
        return await self.db.fetch(
            "SELECT school FROM courses WHERE department = $1", department
        )

    async def fetch_courses(self):
        raw = await self.db.fetch(
            "SELECT code FROM courses WHERE school = $1", self.school
        )
        codes = [i[0] for i in raw]

        return codes

    async def fetch_courses_all(self, course):
        results = {}
        for school in self.SCHOOLS:
            r = await self.db.fetchrow(
                "SELECT * FROM courses WHERE school = $1 AND code = $2", school, course
            )

            if r:
                results[school] = r

        return results

    async def add_course(
        self,
        code,
        number,
        department,
        name,
        description,
        requirements=None,
        academic_level=None,
        units=None,
        campus=None,
    ):
        await self.db.execute(
            "INSERT INTO courses VALUES ($1, $2, $3, $4, $5, $6, $7, %8, $9, $10)",
            self.school,
            code,
            number,
            department,
            name,
            description,
            requirements,
            academic_level,
            units,
            campus,
        )


@asyncinit
class Commands_DB:
    async def __init__(self, guild_id: int):
        """Initalizes self.guild_id & a database connection."""
        self.guild_id = guild_id

        # Grab a database connection
        self.db = await database_connection()

    async def grab_commands(self) -> list:
        """Fetches all of the commands for the server.

        Returns:
            list or None: None if there are no commands otherwise a List of Tuples:
                (
                    command (str), # The name or denominator for the command
                    output (str), # The output message of the command
                    image (None or str) # A link to an image to embed in the command
                )
        """
        commands = []

        commands_db = await self.db.fetch(
            "SELECT command, output, image FROM custom_commands WHERE guild_id = $1",
            self.guild_id,
        )

        for c in commands_db:
            commands.append((c[0], c[1], c[2]))

        try:
            return commands
        except:
            return None

    async def add_command(self, name: str, description: str, image=None):
        """Adds a command to the database.

        Args:
            name (str): The name or denominator for the command.
            description (str): The description or text displayed when the command is called.
            image (str, optional): A link to an image to embed. Defaults to None.
        """

        async with self.db.transaction():
            try:
                await self.db.execute(
                    "INSERT INTO custom_commands VALUES ($1, $2, $3, $4)",
                    self.guild_id,
                    name,
                    description,
                    image,
                )

            except Exception as e:
                print(e)

    async def remove_command(self, command: str):
        """Removes a command from the database.

        Args:
            command (str): The name or denominator for the command.
        """

        async with self.db.transaction():
            try:
                await self.db.execute(
                    "DELETE FROM custom_commands WHERE guild_id = $1 AND command = $2",
                    self.guild_id,
                    command,
                )

            except Exception as e:
                print(e)

    async def fetch_command(self, command):
        return await self.db.fetchrow(
            "SELECT command, output, image FROM custom_commands WHERE guild_id = $1 AND command = $2",
            self.guild_id,
            command,
        )

    async def delete_all_programs(self, user_id):
        await self.db.execute(
            "DELETE FROM programs WHERE guild_id = $1 AND user_id = $2",
            self.guild_id,
            user_id,
        )

    async def update_programs(self, user_id, message):
        await self.db.execute(
            "UPDATE programs SET description = $1 WHERE guild_id = $2 AND user_id = $3",
            message,
            self.guild_id,
            user_id,
        )


@asyncinit
class Guild_DB:
    """The Guild_Info class.  Provides all of the functions required for dealing with the Borg database."""

    async def __init__(self, guild_id: int):
        """Initalizes self.guild_id & a database connection."""
        self.guild_id = guild_id

        # Grab a database connection
        self.db = await database_connection()

    async def grab_settings(self) -> dict:
        """Fetches the server's settings.

        Returns:
            dict or None: Returns None if there are no settings or the server's settings in a dictionary:
                {
                    'programs_channel': int, # The programs channel ID
                    'course_default_school': int # The default school for course selection for this server.
                }
        """

        grab_info = await self.db.fetchrow(
            "SELECT * FROM settings WHERE guild_id = $1", self.guild_id
        )

        if grab_info:
            settings = {
                "programs_channel": grab_info[1],
                "course_default_school": grab_info[2],
            }
            return settings
        else:
            return None

    async def update_settings(self, setting, newvalue):
        await self.db.execute(
            "UPDATE settings SET $1 = $2 WHERE guild_id = $3",
            setting,
            newvalue,
            self.guild_id,
        )

    async def grab_welcome(self) -> dict:
        """Fetches a server's welcome settings.

        Returns:
            dict or None: Returns None if there are no settings or the welcome settings in a dictionary:
                {
                    'channel': int, # The channel ID where welcome messages are provided.
                    'message': str, # The message to welcome a user
                    'enabled': bool # Whether welcome messages are enabled.
                }
        """

        data_pull = await self.db.fetchrow(
            "SELECT * FROM welcome WHERE user_id = $1", self.guild_id
        )

        try:
            welcome = {
                "channel": data_pull[1],
                "message": data_pull[2],
                "enabled": data_pull[3],
            }
            return welcome
        except:
            return None

    async def create_default_settings(self):
        """Creates the default settings value for a guild."""

        async with self.db.transaction():
            try:
                await self.db.execute(
                    "INSERT INTO settings(guild_id, programs_channel, courses_default_school) VALUES ($1, $2, $3)",
                    self.guild_id,
                    None,
                    None,
                )

            except Exception as e:
                print(e)
