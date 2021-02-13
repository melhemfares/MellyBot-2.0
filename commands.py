import discord
from discord.ext import commands
import random

class Commands(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Melly command
    @commands.command()
    async def melly(self, ctx):
        await ctx.send('Melly!')

    #Lunchbox command
    @commands.command()
    async def lunchbox(self, ctx):
        lb_items = ['Granola bar', 
                    'Bear Paws', 
                    'Goldfish crackers',
                    'Dry wrap',
                    'Sideways sandwich',
                    'Broke mac and cheese',
                    'Tabbouleh',
                    'Falafel',
                    'Hummus and pita']
        random_item = random.randint(1, len(lb_items)-1)
        await ctx.send('Oh Mellyyy, what\'s in the lunchbox?')
        await ctx.send(lb_items[random_item])

def setup(client):
    client.add_cog(Commands(client))