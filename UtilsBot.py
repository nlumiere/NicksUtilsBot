import os
import discord
import asyncio
import aiohttp

from dotenv import load_dotenv
from discord.ext import commands

import MathParser as mp
import FarmGame as fg

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents(messages=True, members=True, guilds=True)
bot = commands.Bot(command_prefix='$') # add intents with intents=intents

IMAGE_CATEGS = ['dog', 'cat', 'panda', 'fox', 'red_panda', 'koala', 'birb', 'racoon', 'kangaroo', 'whale', 'pikachu']

@bot.event
async def on_ready():
    for guild in bot.guilds:
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
        a,b = mp.calc(ops)
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
                    color = ctx.author.color
                )
                embed.set_image(url=data['link'])
                await ctx.send(embed=embed)

@bot.command()
async def farm(ctx, *args):
    if args[0] == 'init':
        fg.init(ctx.author)
    
bot.run(TOKEN)
