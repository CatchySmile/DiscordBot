# Discord Nuke Bot v1.6
Hey 👋, this is just a personal project I use myself, go ahead and use it aswell if you want but keep in mind theirs MANY other alternatives.
I only made this because alternatives would Rate limit my account, and im not willing to pay for one that doesnt.

# Preview
![](https://i.ibb.co/bbgbT9F/image.png)

# How to use
Create a bot & find it's token [here](https://discord.com/developers/) (Dont name it something stupid like MEE6 or WICK or DYNO, it will be disabled.)

- Enable these three intents :
![](https://i.ibb.co/QKqyndn/image.png)

- Run `Bot.py`
- Input your bot's token. 
- Type in a guild id then your ready to go.

# Dependencies
 
Run `install.cmd` OR install the following :
```
pip install discord.py
pip install discord
pip install asyncio
pip install sys
pip install aioconsole
pip install json
pip install pystyle
pip install os_sys
```

# Features

-  Send Messages: Send messages to a specific channel within the server.
-  Create Channel(s): Create one or more text channels within the server.
-  Kick User by ID: Kick a user from the server by specifying their user ID.
-  Ban User by ID: Ban a user from the server by specifying their user ID.
-  Unban User by ID: Unban a user from the server by specifying their user ID.
-  Send Message to All Channels: Send a message to all text channels within the server.
-  Delete All Roles: Delete all roles within the server.
-  Delete All Channels: Delete all channels within the server.
-  Kick All Users from Logged IDs: Kick all users from the server whose IDs are logged.
-  Ban All Users from Logged IDs: Ban all users from the server whose IDs are logged. 
-  Log All User Information: Log information about all users in a text file.
-  Log All User IDs: Log the IDs of all users in a JSON file.
-  List All Guilds: List all guilds the bot is currently in.
-  List All Channels: List all channels within the server.
-  Leave Server by ID: Leave a server by specifying its ID.
-  Select Guild ID: Select a specific guild ID for the bot.

# Important!
Because the bot isnt interacting with discord constantly and only does so when given user input, after 15 seconds of no user input the bot will send you a bunch of errors, simply type in option 11 (Log all user id's) so it restores its connection with discord, then continue using the bot.
