# BorgV2

Borg is a modular discord bot that hopes to provide a lot of features that are helpful on University discord servers.  It allows users to display their program applications, lookup a course, and allows server administrators to create custom commands and welcome messages.

## Built With
- [Python](https://www.python.org)
- [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html)
- [Discord.py-slash-commands](https://discord-py-slash-command.readthedocs.io/en/latest/)
- [Postgresql](https://www.postgresql.org/)

And a few other small libraries that can be found in [requirements.txt](https://github.com/joshuajz/Borg/blob/master/requirements.txt).

## Installation

### Database Setup
Borg uses a Postgresql database that you'll need to setup on the machine you use to develop.
1. Install Postgresql -> [Download](https://www.postgresql.org/download/)
2. Change the password of the default `postgresql` username:
```sh
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'newpasswordhere';
# Ensure the result is ALTER ROLE
```
3. Place the database's password in the .env file
4. Start the database:
```sh
sudo service postgresql start
# Result will be similar to: * Starting PostgreSQL 13 database server
```
5. Note your server's port using `sudo service postgresql status`.  The output will be similar to: `13/main (port 5433): online`.  Place the port in the .env file.  You could also run: `sudo netstat -plunt |grep postgres` to get an output of what port(s) postgresql is listening to.
6. NOTE: You can shut down the Postgresql server with `sudo service postgresql stop`

### Borg Setup

#### Install Prerequisites

1. Install [Python](https://www.python.org/downloads/).
2. Clone the repository: `git clone https://github.com/joshuajz/Borg`
3. Install pipenv `pip3 install pipenv`
4. Install the project's requirements: **dev version**: `pipenv install --dev` or if you're planning to run Borg as a server, you'll only need: `pipenv install`
5. If you're developing, you'll now have a virtual environment that you can enable with `pipenv shell`


#### Setup a .env file
A `.env` file should be in your project's directory with the following setup:
```sh
bot_token =
broadcast_token =

database_password =
database_port =

waterloo_api =
```
`bot_token` - The token found on your bot's discord developer portal.
`broadcast_token` - Only used for [message_all_servers.py](https://github.com/joshuajz/Borg/blob/master/helpers/message_all_servers.py)
`database_password` - The password to the `postgresql` user for your database
`database_port` - The port that your database runs on, found with `sudo service postgresql status`
`waterloo_api` - A Waterloo API key used to pull courses from Waterloo.


#### Create a Discord Application
1. Create your own test discord server (press the + at the bottom of your servers list or see [here](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server-)).
2. Create a [Discord Application](https://discord.com/developers/applications) (Click Applications -> New Application).
3. Once in your application, click on the `Bot` tab and scroll slightly to the `Privileged Gateway Intents` section.  Select `PRESENCE INTENT` and `SERVER MEMBERS INTENT` for your test bot.
4. Now we're going to create an invite, click on `OAuth2`, select `bot` and `applications.commands` in the `SCOPES` section.  Then in the `BOT PERMISSIONS` section select the `Administrator` permission (it's easier for a test bot to have all permissions).
5. Using that invite link, invite your test bot to the discord server you created.  You should see your test bot as an offline member.

#### Running Borg
1. Under the `Bot` tab in the Discord Developer Portal there should be a `Token`, select the `Copy` button.
2. Add your token to your bot's .env file
3. Run `python3 main.py` from a terminal.
