import discord
from discord.ext import commands
import os
import json
import random

os.chdir('C:\\Users\\Celeste\\Desktop\\Discord Bots\\MellyBot 2.0')

#Client variable
client = commands.Bot(command_prefix = 'mb.', case_insensitive=True)

#Bot start-up message
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('mb.help | MellyBot 2.0'))
    print('MellyBot 2.0 is ready to go.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.name}: The command you entered does not exist")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.name}: You do not have permission to use that command")

#Loads a cog
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} has been loaded.')

#Unloads a cog
@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} has been unloaded.')

#Reloads a cog
@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} has been reloaded.')  

#Searches cog folder for all the cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

#Client token
token = #No token for you
client.run(token)
