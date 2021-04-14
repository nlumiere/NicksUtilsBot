import os
import discord
import asyncio

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# intents = discord.Intents(messages=True, members=True, guilds=True)
bot = commands.Bot(command_prefix='$') # add intents with intents=intents


MATH_SYMBOLS = ['+', '-', '*', '/', '^', '&', '|', '(', ')', '%']

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
    for i in range(3):
        await asyncio.sleep(10)
        await ctx.send(arg)


def calc(ops):
    i = 0
    rm = 0
    while i < len(ops):
        op = ops[i]
        if op == '(':
            ops[i], rm = calc(ops[i+1:])
            for _ in range(rm):
                ops.pop(i+1)
        elif op == ')':
            slice_ind = i
            rm += i
            ops=ops[:slice_ind]
            break
        i += 1
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == '^':
            ops[i-1] = float(ops[i-1])
            ops[i-1] = ops[i-1] ** float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        i += 1
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == '*':
            ops[i-1] = float(ops[i-1])
            ops[i-1] *= float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '/':
            ops[i-1] = float(ops[i-1])
            ops[i-1] /= float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '&':
            ops[i-1] = int(ops[i-1])
            ops[i-1] &= int(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '|':
            ops[i-1] = int(ops[i-1])
            ops[i-1] |= int(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '%':
            ops[i-1] = int(ops[i-1])
            ops[i-1] %= int(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        i += 1
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == '+':
            ops[i-1] = float(ops[i-1])
            ops[i-1] += float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        elif op == '-':
            ops[i-1] = float(ops[i-1])
            ops[i-1] -= float(ops[i+1])
            ops.pop(i)
            ops.pop(i)
            i -= 1
        i += 1
    if len(ops) > 1:
        return None
    return ops[0], rm+1

# will never contain spaces
def isolate(arg):
    args = []
    zero = 0
    for i in range(len(arg)):
        if arg[i] in MATH_SYMBOLS:
            if i != zero:
                args.append(arg[zero:i])
            args.append(arg[i])
            zero = i+1
    if arg[zero:]:
        args.append(arg[zero:])
    
    return args

def parse(args, searching=False):
    ops = []
    for arg in args:
        isoOps = isolate(arg)
        for op in isoOps:
            ops.append(op)
    
    return ops

@bot.command()
async def math(ctx, *args):
    ops = parse(args, False)
    if ops:
        a,b = calc(ops)
        await ctx.send(a)
    else:
        await ctx.send("Error: Mismatched Parantheses")

@bot.command()
async def resize(ctx, img):
    print(img)
    
bot.run(TOKEN)