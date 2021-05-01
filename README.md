# BorgV2
### About The Project

An advanced discord bot made for university applicant servers that allows users to display their programs.  Also allows administrators to add useful commands and welcome messages.  It's a rewrite of my old bot (Borg).

### Built With
- [Python](https://www.python.org/)
- [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html)
- [Sqlite](https://www.sqlite.org/index.html)

### Installation
**Install Prerequisites:**
1. Install [Python](https://www.python.org/downloads/).
2. Clone the repository:
```sh
git clone https://github.com/joshuajz/BorgV2
```
3. Open the cloned repository
4. Install the prerequisites using pip: (ie. run the following in the cloned folder)
```sh
pip3 install -r requirements.txt
```
**Discord Application Creation**
1. Create a test discord server (ie. press the + in discord).
![image](https://user-images.githubusercontent.com/35657686/112092497-fc912980-8b6d-11eb-994a-be0667b62bc5.png)
2. Create a [discord application](https://discord.com/developers/applications).
3. Create a bot for the discord application by clicking on the "Bot" tab.
4. Scroll slightly down on the "Bot" tab and select the **PRESENCE Intent** and **SERVER MEMBERS Intent**.
![image](https://user-images.githubusercontent.com/35657686/112092380-be940580-8b6d-11eb-9dd7-6f91aa9fdc20.png)
5. Click on OAuth2.
6. Select _bot_ under the Scopes.
7. Select _Administrator_ under the permissions.  Since this is for a test server, we won't worry about selecting only the proper ones.
8. Invite the discord bot to the test server that you've created previously by using the invite link created.
**Running Borg**
1. Under the _Bot_ tab there should be a "Token".  Click the "Copy Token Button"
![image](https://user-images.githubusercontent.com/35657686/114285713-4cedff80-9a27-11eb-967e-52867766ea8e.png)
2. Create a file named .env in the folder's directory.
3. Within that file, add `bot_token=PASTETOEKNHERE`
4. To actually run Borg, run main.py from a terminal.
