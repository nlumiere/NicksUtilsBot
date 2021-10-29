import os
import discord
import asyncio
import aiohttp
import numpy as np
import datetime
import time
import json
import threading

from dotenv import load_dotenv
from discord.ext import commands

import MathParser as mp

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents(messages=True, members=True, guilds=True)
bot = commands.Bot(command_prefix='$', intents=intents)

IMAGE_CATEGS = ['dog', 'cat', 'panda', 'fox', 'red_panda',
                'koala', 'birb', 'racoon', 'kangaroo', 'whale', 'pikachu']
festive_lockout = {}
date_tracking = []


@bot.event
async def on_ready():
    for guild in bot.guilds:
        festive_lockout[str(guild.id)] = 0
        print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )


@bot.command()
async def repeat(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def ping(ctx, arg):
    await ctx.send("Pinging")
    for _ in range(3):
        await asyncio.sleep(10)
        await ctx.send(arg)


@bot.command()
async def math(ctx, *args):
    ops = mp.parse(args, False)
    if ops:
        a, b = mp.calc(ops)
        await ctx.send(a)
    else:
        await ctx.send("Error: Mismatched Parantheses")


@bot.command()
async def image(ctx, arg):
    # IMAGE_CATEGS = ['dog', 'cat', 'panda', 'fox', 'red_panda', 'koala', 'birb', 'racoon', 'kangaroo', 'whale', 'pikachu']
    if str(arg) in IMAGE_CATEGS:
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://some-random-api.ml/img/" + str(arg)) as r:
                data = await r.json()
                embed = discord.Embed(
                    title=str(arg),
                    color=ctx.author.color
                )
                embed.set_image(url=data['link'])
                await ctx.send(embed=embed)


async def make_me_festive(member):
    if member.guild_permissions.administrator:
        return False
    if member.display_name.lower().startswith('festive'):
        await member.edit(nick=member.display_name[7:])
    elif member.display_name.lower().startswith('festive '):
        await member.edit(nick=member.display_name[8:])
    else:
        await member.edit(nick="Festive " + member.display_name)
    return True


async def festive_remove(ctx):
    for member in ctx.guild.members:
        for role in member.roles:
            if role.name.lower().startswith('festive'):
                await member.remove_roles(role)


async def festive_swap(ctx, roles):
    working_roles = []
    await ctx.send("Swapping Roles!")
    for role in ctx.guild.roles:
        if role.name in roles:
            working_roles.append(role)
    for member in ctx.guild.members:
        for role in member.roles:
            if role.name.lower().startswith('festive'):
                await member.remove_roles(role)
        random_role = np.random.choice(working_roles)
        await member.add_roles(random_role)


@bot.command()
async def festive(ctx, arg=""):
    global festive_lockout
    roles = ['FestiveGreen', 'FestiveRed']
    if str(arg).lower() == 'me':
        if not await make_me_festive(ctx.message.author):
            await ctx.send("Cannot change nickname of administrator. Change it yourself.")
        return
    elif str(arg).lower() == 'remove':
        await festive_remove(ctx)
        return
    elif str(arg).lower() == 'white':
        roles.append('FestiveWhite')

    timestamp = datetime.datetime.now().timestamp()
    if timestamp - festive_lockout[str(ctx.guild.id)] < 100:
        await ctx.send("You must wait another " + str(100 - (timestamp-festive_lockout[str(ctx.guild.id)])//1) + " seconds to start festivities.")
        return
    festive_lockout[str(ctx.guild.name)] = timestamp

    await festive_swap(ctx, roles)


# TODO: Only load the specific guild ctx references.
@bot.command()
async def birthday(ctx, *args):
    infile = open('birthdays.json', 'r')
    data = json.load(infile)
    # $birthday
    if len(args) == 0:
        if str(ctx.guild.id) in data:
            if str(ctx.message.author.id) in data[str(ctx.guild.id)]:
                buildstr = "<@" + str(ctx.message.author.id) + \
                    ">'s birthday is: " + \
                    data[str(ctx.guild.id)][str(ctx.message.author.id)]
                await ctx.send(buildstr)
        else:
            await ctx.send("Guild not registered")
    elif len(args) > 2:
        await ctx.send("`birthday set/[display name] date (m/d/yyyy)`")
    # $birthday set 1/2/2000
    elif args[0] == 'set':
        if not str(ctx.guild.id) in data:
            data[str(ctx.guild.id)] = {}
        try:
            date = datetime.datetime.strptime(args[1], '%m/%d/%Y').date()
            data[str(ctx.guild.id)][str(ctx.message.author.id)] = str(date)
            print(data)
            with open('birthdays.json', 'w') as outfile:
                json.dump(data, outfile)
        except:
            await ctx.send("`birthday set/[display name] date (m/d/yyyy)`")
    # $birthday toggle
    elif args[0].lower() == 'toggle':
        if ctx.guild in date_tracking:
            date_tracking.remove(ctx.guild)
            await ctx.send("Birthday messaging in this server turned **off**")
        else:
            date_tracking.append(ctx.guild)
            await ctx.send("Birthday messaging in this server turned **on**")
            if str(ctx.guild.id) not in data:
                data[str(ctx.guild.id)] = {}
            await track_time_runner(ctx)
    # $birthday [username]
    elif args[0].lower() in [member.display_name.lower() for member in ctx.guild.members]:
        if str(ctx.guild.id) in data:
            for member in ctx.guild.members:
                if args[0].lower() == member.display_name.lower() and str(member.id) in data[str(ctx.guild.id)]:
                    buildstr = "<@" + str(ctx.message.author.id) + \
                        ">'s birthday is: " + \
                        data[str(ctx.guild.id)][str(member.id)]
                    await ctx.send(buildstr)
        else:
            await ctx.send("Guild not registered")


async def track_time_runner(ctx):
    while(True):
        now_datetime = datetime.datetime.now()
        if np.floor(datetime.datetime.timestamp(now_datetime)) % 86400 == 28800:
            # if np.floor(datetime.datetime.timestamp(now_datetime)) % 3600 == 0:
            infile = open('birthdays.json', 'r')
            data = json.load(infile)
            for guild in date_tracking:
                guild_data = data[str(guild.id)]
                for member in guild_data:
                    birthday = guild_data[member]
                    birthday_datetime = datetime.datetime.strptime(
                        birthday, "%Y-%m-%d")
                    if birthday_datetime.month == now_datetime.month and birthday_datetime.day == now_datetime.day:
                        buildstr = "Happy Birthday <@" + str(member) + ">!"
                        await ctx.send(buildstr)
        await asyncio.sleep(1)


bot.run(TOKEN)
