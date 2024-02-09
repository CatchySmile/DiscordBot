from discord.ext import commands
from discord.ext import commands, tasks
import discord
import asyncio
import sys
import aioconsole
import json
import pystyle
import os
from pystyle import Write, Colors
from discord import Status
from discord import Status, Activity

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

client = commands.Bot(command_prefix='?', intents=intents, reconnect=True)

guild_id = None

@client.event
async def on_message(message):
    if message.author == client.user:
        return 

    await client.process_commands(message)

async def send_message():
    channel_id = int(Write.Input("Enter the channel ID to send the message. [1] To return to options:  ",Colors.cyan, interval=0))
    channel = client.get_channel(channel_id)

    if channel:
        while True:
            message_content = Write.Input("Enter the message to send. [F] To return to options: ",Colors.cyan, interval=0.00005)

            if message_content.lower() == 'exit':
                break

            if message_content.lower() == 'f':
                Write.Print("Returning to options...",Colors.red, interval=0.00005)
                break

            await channel.send(message_content)
    else:
        Write.Print(f"Channel with ID {channel_id} not found.", Colors.red, interval=0)

async def create_channels():
    global guild_id
    guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)

    if guild:
        channel_name = Write.Input("Enter the name for the new channels. [F] To return to options: ",Colors.cyan, interval=0)

        if channel_name.lower() == 'exit':
            return

        if channel_name.lower() == 'f':
            Write.Print("Returning to options...",Colors.red, interval=0.00005)
            return

        try:
            num_channels = int(Write.Input("Enter the number of channels to create: ",Colors.blue, interval=0.00005))
        except ValueError:
            Write.Print("Invalid input. Please enter a valid number.",Colors.cyan, interval=0)
            return
            
        for i in range(num_channels):
            await guild.create_text_channel(f"{channel_name}_{i + 1}")

        Write.Print(f"{num_channels} channels with the name '{channel_name}' created successfully!",Colors.cyan, interval=0)
    else:
        Write.Print(f"Bot is not in a guild with ID {guild_id}. (Did you forget to select one?)",Colors.red, interval=0)


async def kick_user_by_id(guild, user_id):
    try:
        user = await guild.fetch_member(user_id)
        await user.kick(reason="Kicked by bot")
        Write.Print(f"User {user.name} with ID {user.id} kicked successfully.\n",Colors.red, interval=0)
    except discord.NotFound:
        Write.Print(f"User with ID {user_id} not found.\n",Colors.red, interval=0)
    except discord.Forbidden:
        Write.Print("Bot does not have the permission to kick the user.\n",Colors.red, interval=0)
    except Exception as e:
        print(f"An error occurred: {e}")

async def ban_user_by_id(guild, user_id):
    try:
        user = await guild.fetch_member(user_id)
        await user.ban(reason="Banned by bot")
        Write.Print(f"User {user.name} with ID {user.id} banned successfully.\n",Colors.red, interval=0)
    except discord.NotFound:
        Write.Print(f"User with ID {user_id} not found.\n",Colors.red, interval=0)
    except discord.Forbidden:
        Write.Print("Bot does not have the permission to ban the user.\n",Colors.red, interval=0)
    except Exception as e:
        print(f"An error occurred: {e}")

async def change_guild_id():
    Write.Print(f'\nSelectable Guilds:\n', Colors.blue, interval=0)
    for guild in client.guilds:
         Write.Print(f"ID: {guild.id}, Name: {guild.name}\n", Colors.cyan, interval=0)
    global guild_id
    new_guild_id = int(Write.Input("Enter the new guild ID: ",Colors.blue, interval=0))
    guild = discord.utils.find(lambda g: g.id == new_guild_id, client.guilds)
    
    if guild:
        guild_id = new_guild_id
        Write.Print(f"Guild ID updated to {new_guild_id}.",Colors.cyan, interval=0)
    else:
        Write.Print(f"Bot is not in a guild with ID {new_guild_id}.",Colors.red, interval=0)
        

async def log_all_user_ids(guild):
    try:
        data = {"guild_id": guild.id, "members": []}

        for member in guild.members:
            member_data = {"name": member.name, "id": member.id}
            data["members"].append(member_data)

        with open('user_ids_log.json', 'w') as file:
            json.dump(data, file, indent=4)

        Write.Print("User IDs logged successfully.",Colors.cyan, interval=0)
    except Exception as e:
        Write.Print(f"An error occurred while logging user IDs: {e}",Colors.yellow, interval=0)

async def kick_all_users(guild):
    try:
        with open('user_ids_log.json', 'r') as file:
            data = json.load(file)

            for member_data in data["members"]:
                user_id = member_data["id"]
                await kick_user_by_id(guild, user_id)

        Write.Print("All users kicked successfully.",Colors.cyan, interval=0)
    except Exception as e:
        print(f"An error occurred while kicking all users: {e}")

async def ban_all_users(guild, exclude_ids=None):
    try:
        with open('user_ids_log.json', 'r') as file:
            data = json.load(file)

            for member_data in data["members"]:
                user_id = member_data["id"]

                if exclude_ids and user_id in exclude_ids:
                    Write.Print(f"User with ID {user_id} excluded from ban.", Colors.yellow, interval=0)
                    continue

                await ban_user_by_id(guild, user_id)
                await asyncio.sleep(0.45)  # 250ms delay between bans

        Write.Print("All users banned successfully.", Colors.cyan, interval=0)
    except Exception as e:
        Write.Print(f"An error occurred while banning all users: {e}", Colors.red, interval=0)

async def unban_user_by_id(guild, user_id):
    try:
        user = await guild.fetch_ban(discord.Object(id=user_id))
        await guild.unban(user.user, reason="Unbanned by bot")
        Write.Print(f"User {user.user.name} with ID {user.user.id} unbanned successfully.\n",Colors.cyan, interval=0)
    except discord.NotFound:
        Write.Print(f"User with ID {user_id} not found in ban list.\n",Colors.red, interval=0)
    except discord.Forbidden:
        Write.Print("Bot does not have the permission to unban the user.\n",Colors.red, interval=0)
    except Exception as e:
        print(f"An error occurred: {e}")

async def delete_all_channels(guild):
    try:
        for channel in guild.channels:
            try:
                await channel.delete()
                Write.Print(f"Channel '{channel.name}' (ID: {channel.id}) deleted successfully.\n",Colors.cyan, interval=0)
            except discord.Forbidden:
                Write.Print(f"Bot does not have permission to delete channel '{channel.name}' (ID: {channel.id}). Skipping...",Colors.red, interval=0)
            except Exception as e:
                Write.Print(f"An error occurred while deleting channel '{channel.name}' (ID: {channel.id}): {e}",Colors.red, interval=0)
    except Exception as e:
        Write.Print(f"An error occurred while iterating over channels: {e}",Colors.yellow, interval=0)


async def delete_all_roles(guild):
    try:
        for role in guild.roles:
            try:
                await role.delete()
                Write.Print(f"Role '{role.name}' deleted successfully.\n",Colors.cyan, interval=0)
            except discord.Forbidden:
                Write.Print(f"Bot does not have the permission to delete role '{role.name}'.\n",Colors.red, interval=0)
            except Exception as e:
                Write.Print(f"An error occurred while deleting role '{role.name}': {e}\n",Colors.red, interval=0)
    except Exception as e:
        Write.Print(f"An error occurred while iterating over roles: {e}",Colors.yellow, interval=0)

async def list_all_guilds():
    Write.Print("\nList of Guilds:\n",Colors.blue, interval=0)
    for guild in client.guilds:
         Write.Print(f"ID: {guild.id}, Name: {guild.name}\n", Colors.cyan, interval=0)

async def list_all_channels(guild):
    print("List of Channels:")
    for channel in guild.channels:
        channel_type = ''
        if isinstance(channel, discord.CategoryChannel):
            channel_type = '[Category]'
        elif isinstance(channel, discord.TextChannel):
            channel_type = '[Text]'
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = '[VC]'

        print(f"ID: {channel.id} | Name: {channel.name} {channel_type}")


async def leave_server_by_id():
    global guild_id
    Write.Print(f'\nSelectable Guilds:\n', Colors.blue, interval=0)
    for guild in client.guilds:
        Write.Print(f"ID: {guild.id}, Name: {guild.name}\n", Colors.cyan, interval=0)
    guild_to_leave_id = int(Write.Input("\nEnter the guild ID to leave: ",Colors.red, interval=0))
    guild_to_leave = discord.utils.find(lambda g: g.id == guild_to_leave_id, client.guilds)

    if guild_to_leave:
        await guild_to_leave.leave()
        Write.Print(f"Bot has left the guild with ID {guild_to_leave_id}.",Colors.cyan, interval=0)
    else:
        Write.Print(f"Bot is not in a guild with ID {guild_to_leave_id}. (Typo?)",Colors.cyan, interval=0)



async def send_message_to_all_channels(guild):
    message_content = Write.Input("Enter the message to send to all channels. [F] To return to options: ",Colors.cyan, interval=0.00005)

    if message_content.lower() == 'f':
        Write.Print("Returning to options...",Colors.red, interval=0.00005)
        return

    try:
        num_messages_per_channel = int(Write.Input("\nEnter the number of messages to send per channel: ",Colors.cyan, interval=0.00005))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]

    for i in range(num_messages_per_channel):
        for channel in text_channels:
            try:
                await channel.send(message_content)
                await asyncio.sleep(0.1)  # 0.1 second delay between messages
            except discord.Forbidden:
                Write.Print(f"Bot does not have permission to send messages in channel '{channel.name}' (ID: {channel.id}). Skipping...",Colors.red, interval=0)
            except Exception as e:
                print(f"An error occurred while sending a message to channel '{channel.name}' (ID: {channel.id}): {e}",Colors.yellow, interval=0)

    print(f"{num_messages_per_channel} messages sent to all text channels successfully.")

async def log_all_user_info(guild):
    try:
        data = {"users": []}

        for member in guild.members:
            user_data = {
                "id": member.id,
                "username": member.name,
                "display_name": member.display_name,
                "mutual_servers": [server.name for server in client.guilds if member in server.members and server != guild],
                "badges": [badge.name for badge in member.public_flags.all()],
                "creation_date": member.created_at.isoformat(),
                "joined_date": member.joined_at.isoformat() if member.joined_at else None,
                "status": str(member.status),
                "activities": [activity.name for activity in member.activities if isinstance(activity, Activity)]
            }
            data["users"].append(user_data)

        # Load existing data if the file exists
        try:
            with open('user_info.txt', 'r') as existing_file:
                existing_data = json.load(existing_file)
                data["users"].extend(existing_data["users"])
        except FileNotFoundError:
            pass

        with open('user_info.txt', 'w') as file:
            json.dump(data, file, indent=4)

        Write.Print("User information logged successfully.",Colors.cyan, interval=0)
    except Exception as e:
        Write.Print(f"An error occurred while logging user information: {e}\n", Colors.yellow, interval=0)
        Write.Print(f"Maybe the file is corrupt? (Common fix is delete user_info.txt)\n", Colors.yellow, interval=0)




async def options_menu():
    global guild_id

    while True:
        Write.Print("\n╔═══════════════════════════════════════════════════════════════════════════════════════╗\n", Colors.pink, interval=0)
        Write.Print("║                                      Options Menu                                     ║\n", Colors.pink, interval=0)
        Write.Print("╟───────────────────────────────────────────╥───────────────────────────────────────────╢\n", Colors.pink, interval=0)
        Write.Print("║ 1. Send Messages                          ║ 11. Log All User Information              ║\n", Colors.red, interval=0)
        Write.Print("║ 2. Create Channel(s)                      ║ 12. Log All User IDs                      ║\n", Colors.red, interval=0)
        Write.Print("║ 3. Kick User by ID                        ║ 13. List All Guilds                       ║\n", Colors.red, interval=0)
        Write.Print("║ 4. Ban User by ID                         ║ 14. List All Channels                     ║\n", Colors.red, interval=0)
        Write.Print("║ 5. Unban User by ID                       ║ 15. Leave Server by ID                    ║\n", Colors.red, interval=0)
        Write.Print("║ 6. Send Message to All Channels           ║ 16.                                       ║\n", Colors.red, interval=0)
        Write.Print("╠═══════════════════════════════════════════╬═══════════════════════════════════════════╣\n", Colors.red, interval=0)
        Write.Print("║ 7. Delete All Roles                       ║ 17.                                       ║\n", Colors.red, interval=0)
        Write.Print("║ 8. Delete All Channels                    ║ 18.                                       ║\n", Colors.red, interval=0)
        Write.Print("║ 9. Kick All Users from Logged IDs         ║ 19.                                       ║\n", Colors.red, interval=0)
        Write.Print("║ 10. Ban All Users from Logged IDs         ║ 20. Select Guild ID                       ║\n", Colors.red, interval=0)
        Write.Print("╠═══════════════════════════════════════════╬═══════════════════════════════════════════╣\n", Colors.red, interval=0)
        Write.Print("║ 0. Log off                                ║ 100. Full nuke [Coming soon]              ║\n", Colors.red, interval=0)
        Write.Print("╚═══════════════════════════════════════════╩═══════════════════════════════════════════╝\n", Colors.red, interval=0)

        choice = Write.Input("Enter choice: ", Colors.blue, interval=0)

        if choice == '0':
            print("Fatal Error : Terminating Connection")
            return
        elif choice == '1':
            await send_message()
        elif choice == '2':
            await create_channels()
        elif choice == '3':
            user_id = int(Write.Input("Enter the user ID to kick: ",Colors.cyan, interval=0))
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await kick_user_by_id(guild, user_id)
        elif choice == '4':
            user_id = int(Write.Input("Enter the user ID to ban: ",Colors.cyan, interval=0))
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await ban_user_by_id(guild, user_id)
        elif choice == '5':
            user_id = int(Write.Input("Enter the user ID to unban: ",Colors.cyan, interval=0))
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await unban_user_by_id(guild, user_id)
        elif choice == '6':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await send_message_to_all_channels(guild)
        elif choice == '7':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await delete_all_roles(guild)
        elif choice == '8':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await delete_all_channels(guild)
        elif choice == '9':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await kick_all_users(guild)
        elif choice == '10':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            exclude_ids_input = Write.Input("Enter the user IDs to exclude (comma-separated): ",Colors.cyan, interval=0.00005)
            exclude_ids = [int(id.strip()) for id in exclude_ids_input.split(',') if id.strip().isdigit()]
            await ban_all_users(guild, exclude_ids)
        elif choice == '11':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await log_all_user_info(guild)
        elif choice == '12':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await log_all_user_ids(guild)
        elif choice == '13':
            await list_all_guilds()
        elif choice == '14':
            guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
            await list_all_channels(guild)
        elif choice == '15':
            await leave_server_by_id()

        elif choice == '20':
            await change_guild_id()
        else:
            Write.Print("Invalid choice. Please try again.",Colors.yellow, interval=0)
        await asyncio.sleep(1)

@client.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    global guild_id
    Write.Print(f'\nLogged in as ', Colors.blue, interval=0)
    Write.Print(f'"{client.user}"', Colors.orange, interval=0.005)
    print(f'\n ')


    skip_guild_id = Write.Input("\nDo you want to skip entering the Guild ID? (yes/no): ", Colors.blue, interval=0.00005).lower()
    
    if skip_guild_id == 'no':
        Write.Print(f'\nSelectable Guilds:\n', Colors.blue, interval=0)
        for guild in client.guilds:
            Write.Print(f"ID: {guild.id}, Name: {guild.name}\n", Colors.cyan, interval=0)
        guild_id = int(Write.Input("\nEnter Guild ID: ", Colors.blue, interval=0.00005))
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)

        if guild:
            os.system('cls' if os.name == 'nt' else 'clear')
            Write.Print(f'Selected Guild:', Colors.blue, interval=0)
            Write.Print(f' - {guild.name} (ID: {guild.id})', Colors.yellow, interval=0)
            Write.Print(f'\nAll Guilds:\n', Colors.blue, interval=0)
            for guild in client.guilds:
                Write.Print(f"ID: {guild.id}, Name: {guild.name}\n", Colors.cyan, interval=0)

            # Dictionary mapping user IDs to their corresponding messages
            user_id_messages = {
                651095740390834176: "Warning: This server contains a bot with the ID '651095740390834176', which belongs to Securitybot.gg and WILL block ALOT of attempts to modify the guild.",
                957481307405975552: "Warning: This server contains a bot with the ID '957481307405975552', which belongs to Good Knight and may block attempts to modify the guild.",
                512333785338216465: "Warning: This server contains a bot with the ID '512333785338216465', which belongs to Captcha.bot and may block attempts to modify the guild."
            }

            for member_id, message in user_id_messages.items():
                member_with_specific_id = discord.utils.get(guild.members, id=member_id)
                if member_with_specific_id:
                    print(message)

            await options_menu()
        else:
            print(f'Bot is not in a guild with ID {guild_id}. (Typo?) Exiting...')
    else:
        print("Skipping Guild ID entry. You can set the Guild ID later.")
        await options_menu()



try:
    os.system('cls' if os.name == 'nt' else 'clear')
    token = Write.Input("\nEnter your bot token: ",Colors.blue, interval=0.000005)
    client.run(token)
except KeyboardInterrupt:
    print("Bot stopped manually. Exiting...")
finally:
    print("Fatal Error : Terminating Connection")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.close())