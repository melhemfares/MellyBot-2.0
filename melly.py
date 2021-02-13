import discord
from discord.ext import commands
import random
import asyncio

class Melly(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Send Melly command
    @commands.command()
    async def sendmelly(self, ctx):
        max = 210
        rand = random.randint(1, max)
        while (rand == 52):
            rand = random.randint(1, max)

        await ctx.send(file=discord.File(f'photos/mb{rand}.png'))

def setup(client):
    client.add_cog(Melly(client))