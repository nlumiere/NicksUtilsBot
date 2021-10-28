import os
import discord
import asyncio
import aiohttp
import numpy as np
import datetime

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


@bot.event
async def on_ready():
    for guild in bot.guilds:
        festive_lockout[guild.name] = 0
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
    if timestamp - festive_lockout[ctx.guild.name] < 100:
        await ctx.send("You must wait another " + str(100 - (timestamp-festive_lockout[ctx.guild.name])//1) + " seconds to start festivities.")
        return
    festive_lockout[ctx.guild.name] = timestamp

    await festive_swap(ctx, roles)

bot.run(TOKEN)
