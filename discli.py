# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                         #
#  discli                                                                 #
#  Copyright (C) 2022 giantfroje                                          #
#                                                                         #
#  This program is free software: you can redistribute it and/or modify   #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation, either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful,        #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#  GNU General Public License for more details.                           #
#                                                                         #
#  You should have received a copy of the GNU General Public License      #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#                                                                         #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys
import asyncio

import json

import curses
from curses.textpad import rectangle

import discord



channel = None
ready = False


def load_config():
    default_config = json.loads('{"token": "<Token Here>"}')
    config = {}

    noconfig = False

    try:
        f = open("config.json", "r")
        config = json.loads(f.readline())
        f.close()
    except (FileNotFoundError, json.JSONDecodeError):
        config = default_config
        noconfig = True

    notoken = "token" not in config

    if notoken:
        config["token"] = default_config["token"]

    f = open("config.json", "w")
    f.write(json.dumps(config))
    f.close()

    if noconfig:
        print("\"config.json\" not found, creating from default")
        sys.exit(69)

    if notoken:
        config = default_config
        print("\"config.json\" did not contain \"token\" field, creating from default")
        sys.exit(68)

    return config

def start_discord_client():
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    return client

def create_discord_events(discord_client): # NEEDS REFACTORING - Later parts rely on the bad parts
    @client.event
    async def on_ready():
        client.loop.create_task(main())

    @client.event  
    async def on_message(message):
        if ready:
            if channel != None:
                if message.channel.id == channel.id:
                    load_messages(stdscr, message.channel)


def start_curses():
    stdscr = curses.initscr()
    stdscr.nodelay(True)
    stdscr.keypad(True)

    curses.noecho()
    curses.cbreak()

    return stdscr

def stop_curses(stdscr):
    stdscr.keypad(False)

    curses.nocbreak()
    curses.echo()
    curses.endwin()

def create_ui(stdscr):
    stdscr.clear()

    # Servers
    rectangle(stdscr, 0,0, curses.LINES-1, 33)
    stdscr.addstr(0,2, "Servers")

    # Channels
    rectangle(stdscr, 0,35, curses.LINES-1, 68)
    stdscr.addstr(0,37, "Channels")

    # Main
    rectangle(stdscr, 0,70, curses.LINES-1, curses.COLS-44)
    stdscr.addstr(0,72, "discli")

    # Message Box
    stdscr.addstr(curses.LINES-3,70, "├" + ("─" * (curses.COLS-115)) + "┤")
    stdscr.addstr(curses.LINES-2,71, "$")

    # Users
    rectangle(stdscr, 0,curses.COLS-42, curses.LINES-1, curses.COLS-2)
    stdscr.addstr(0,curses.COLS-40, "Users")

    stdscr.refresh()


async def load_guilds(stdscr, client, offset = 0, highlight = 0):
    guilds = client.guilds
    i = offset
    for j in range(len(guilds) if len(guilds) < curses.LINES-2 else curses.LINES-2):
        name = guilds[i].name if len(guilds[i].name) <= 32 else guilds[i].name[:29] + "..."
        name += " " * (32 - len(name))
        stdscr.addstr(1 + i - offset, 1, name)
        i += 1



    name = guilds[highlight].name if len(guilds[highlight].name) <= 32 else guilds[highlight].name[:29] + "..."
    name += " " * (32 - len(name))
    stdscr.addstr(1 + highlight - offset, 1, name, curses.A_REVERSE)

    return guilds

async def load_members(stdscr, guild):
    for i in range(curses.LINES-2):
        stdscr.addstr(curses.LINES - 2 - i, curses.COLS - 40, " " * 38)

    members = guild.members
    for i in range(len(members) if len(members) < curses.LINES-2 else curses.LINES-2):
        member = members[i];
        name = "@" + member.name + "#" + member.discriminator
        if member.bot:
            name += " [BOT]"
        stdscr.addstr(1 + i, curses.COLS-40, name)

async def load_channels(stdscr, guild, offset = 0, highlight = 0):
    for i in range(curses.LINES-2):
        stdscr.addstr(curses.LINES - 2 - i, 36, " " * 32)

    channels = []
    i = 0
    for channel in guild.channels:
        if channel.type == discord.ChannelType.text:
            channels.append((i, channel))
            i += 1
    channels.sort(key=lambda x: x[1].position)

    i = offset
    for j in range(len(channels) if len(channels) < curses.LINES - 2 else curses.LINES - 2):
        name = channels[i][1].name if len(channels[i][1].name) <= 31 else channels[i][1].name[:28] + "..."
        stdscr.addstr(1 + i - offset, 36, "#" + name)
        i += 1

    name = channels[highlight][1].name if len(channels[highlight][1].name) <= 31 else channels[highlight][1].name[:28] + "..."
    name += " " * (31 - len(name))
    stdscr.addstr(1 + highlight - offset, 36, "#" + name, curses.A_REVERSE)

    return channels

async def load_messages(stdscr, channel):
    for i in range(curses.LINES-4):
        stdscr.addstr(curses.LINES - 4 - i, 71, " " * (curses.COLS - 115))

    i = 0
    async for message in channel.history(limit=curses.LINES-4):
        stdscr.addstr(curses.LINES - 4 - i, 71, message.created_at.strftime("%d/%m/%Y %H:%M:%S") + " | " + message.author.name + "> " + message.content)
        i += 1


async def send_message(message, channel):
    if message.startswith("/shrug ") or message == "/shrug":
        message = message[7:]
        message += " ¯\_(ツ)_/¯"
    elif message.startswith("/flip ") or message == "/flip":
        message = message[6:]
        message += " (╯°□°）╯︵ ┻━┻"
    elif message.startswith("/unflip ") or message == "/unflip":
        message = message[8:]
        message += " ┬─┬ ノ( ゜-゜ノ)"
    await channel.send(message)

async def process_command(command):
    if command == "quit" or command == "q":
        await client.close()
    elif command == "servers" or command == "s" or command == "guilds" or command == "g":
        control_state = 2
        curses.curs_set(0)
    elif command == "channels" or command == "c":
        control_state = 1
        curses.curs_set(0)
    elif command.startswith("echo "):
        await channel.send(command[5:])
    elif command.startswith("test"):
        await switch_channel(guild.get_channel(935451583553093672))
    elif command.startswith("chardb"):
        control_state = -1

    return control_state

async def main():
    stdscr = start_curses()
    create_ui(stdscr)

    global ready

    control_state = 0
    is_console = True

    global channel
    channels = None
    new_channel = None
    channel_index = 0
    new_channel_index = 0
    channel_scroll_pos = 0
    new_channel_scroll_pos = 0
    
    guild = None
    guilds = await load_guilds(stdscr, client)
    new_guild = None
    guild_index = 0
    new_guild_index = 0
    guild_scroll_pos = 0
    new_guild_scroll_pos = 0

    cursor = 0
    message = ""

    ready = True
    while client.is_ready():
        key = stdscr.getch()

        if key == 410: # resize
            await client.close()

        if control_state == -1: # key debug
            if key == 27: # escape
                control_state = 0
            stdscr.addstr(curses.LINES-2,1+32+1 +1 +2 +1+32+1 + 2, str(key) + " " * 10)
            stdscr.refresh()
            await asyncio.sleep(2)
            continue
        elif control_state == 0: # regular input
            if key == 353 or key == 9:
                if is_console:
                    stdscr.addstr(curses.LINES-2,71, ">")
                    is_console = False
                else:
                    stdscr.addstr(curses.LINES-2,71, "$")
                    is_console = True
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                message = message[:-1]
                cursor -= 1
                if cursor < 0:
                    cursor = 0
            elif key == curses.KEY_ENTER or key == 10:
                if is_console:
                    control_state = await process_command(message)
                    stdscr.addstr(curses.LINES - 2, 71, ">")
                    is_console = False
                else:
                    await send_message(message, channel)
                message = ""
                cursor = 0
            elif key == curses.KEY_LEFT:
                cursor -= 1
                if cursor < 0:
                    cursor = 0
            elif key == curses.KEY_RIGHT:
                cursor += 1
                if cursor > len(message):
                    cursor = len(message)
            elif key == -1:
                pass
            else:
                message_split = list(message)
                message_split.insert(cursor, chr(key))
                message = "".join(message_split)
                cursor += 1
                if cursor > len(message):
                    cursor = len(message)

            stdscr.addstr(curses.LINES-2,73, (" " * (curses.COLS-40 - 77)))
            stdscr.addstr(curses.LINES-2,73, message)
            stdscr.move(curses.LINES-2,73 + cursor)
        elif control_state == 1: # channel scrolling
            if key == curses.KEY_ENTER or key == 10:
                channel_index = new_channel_index
                channel_scroll_pos = new_channel_scroll_pos
                channel = new_channel

                await load_messages(stdscr, channel)

                curses.curs_set(1)
                stdscr.move(curses.LINES-2,73 + cursor)
                control_state = 0
            elif key == 27: # escape
                if channel != None:
                    new_channel_index = channel_index
                    new_channel_scroll_pos = channel_scroll_pos

                    await load_channels(stdscr, guild, channel_scroll_pos, channel_index)
                    curses.curs_set(1)
                    stdscr.move(curses.LINES-2,73 + cursor)
                    control_state = 0
            elif key == curses.KEY_UP:
                new_channel_index -= 1
                if new_channel_index < 0:
                    new_channel_index += 1
                elif new_channel_index - new_channel_scroll_pos < 0:
                    new_channel_scroll_pos -= 1

                new_channel = channels[new_channel_index][1]

                await load_channels(stdscr, guild, new_channel_scroll_pos, new_channel_index)
            elif key == curses.KEY_DOWN:
                new_channel_index += 1
                if new_channel_index >= len(channels):
                    new_channel_index -= 1
                elif new_channel_index - new_channel_scroll_pos >= curses.LINES -2:
                    new_channel_scroll_pos += 1
                
                new_channel = channels[new_channel_index][1]

                await load_channels(stdscr, guild, new_channel_scroll_pos, new_channel_index)
            elif new_channel == None:
                new_channel = channels[0][1]
                name = channels[0][1].name if len(channels[0][1].name) <= 31 else channels[0][1].name[:28] + "..."
                name += " " * (31 - len(name))
                stdscr.addstr(1, 36, "#" + name, curses.A_REVERSE)
        elif control_state == 2: # guild scrolling
            if key == curses.KEY_ENTER or key == 10:
                guild_index = new_guild_index
                guild_scroll_pos = new_guild_scroll_pos
                guild = guilds[guild_index]

                channel_index = 0
                channel_scroll_pos = 0
                new_channel_index = 0
                new_channel_scroll_pos = 0

                await load_members(stdscr, guild)
                channels = await load_channels(stdscr, guild)

                control_state = 1
            elif key == 27: # escape
                if guild != None:
                    new_guild_index = guild_index
                    new_guild_scroll_pos = guild_scroll_pos
                    
                    await load_guilds(stdscr, client, guild_scroll_pos, guild_index)

                    curses.curs_set(1)
                    stdscr.move(curses.LINES-2,73 + cursor)
                    control_state = 0
            elif key == curses.KEY_UP:
                new_guild_index -= 1
                if new_guild_index < 0:
                    new_guild_index += 1
                elif new_guild_index - new_guild_scroll_pos < 0:
                    new_guild_scroll_pos -= 1

                new_guild = guilds[new_guild_index]
                
                await load_guilds(stdscr, client, new_guild_scroll_pos, new_guild_index)
            elif key == curses.KEY_DOWN:
                new_guild_index += 1
                if new_guild_index >= len(guilds):
                    new_guild_index -= 1
                elif new_guild_index - new_guild_scroll_pos >= curses.LINES -2:
                    new_guild_scroll_pos += 1
                

                new_guild = guilds[new_guild_index]

                await load_guilds(stdscr, client, new_guild_scroll_pos, new_guild_index)
            elif new_guild == None:
                name = guilds[0].name if len(guilds[0].name) <= 32 else guilds[0].name[:29] + "..."
                name += " " * (32 - len(name))
                stdscr.addstr(1, 1, name, curses.A_REVERSE)
        else:
            control_state = 0

        stdscr.refresh()
        await asyncio.sleep(0.01)



config = load_config()
client = start_discord_client()
create_discord_events(client)

try:
    client.run(config["token"], bot=False)
except (discord.errors.LoginFailure):
    print("Invalid token")
    sys.exit(70)

stop_curses(stdscr)