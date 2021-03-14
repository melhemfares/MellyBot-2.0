# -------- PROFILE COMMANDS --------

import discord
from discord.ext import commands
import json
import random
import os
from .economy import *

os.chdir('C:\\Users\\fares\\Desktop\\Discord Bots\\MellyBot 2.0\\cogs')

class Profile(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on a cooldown. Try again in `%.2fs` second(s)." % error.retry_after)
        else:
            raise error

    #Daily claim command
    @commands.command(aliases=['daily'], help="Collect your daily claim")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def claim(self, ctx):

        await open_account(ctx.author)
        await open_profile(ctx.author)
        users = await get_bank_data()
        user = ctx.author

        bal = await update_bank(ctx.author)
        profile = await update_profile(ctx.author)

        earnings = int(500 + (profile[1] * 500))
        await ctx.send(f"{ctx.author.mention}: You claimed your daily claim. You earned {earnings}MM!")

        users[str(user.id)]['wallet'] += earnings

        with open('user_data.json', 'w') as f:
            json.dump(users, f)
        return True

    #Profile command
    @commands.command(aliases=['level', 'lvl', 'exp'], help="Check what level you are")
    async def profile(self, ctx, member:discord.Member=None):

        if member == None:
            member = ctx.author

        await open_profile(member)
        users = await get_profile_data()
        user = member

        profile = await update_profile(member)

        lvl_amt = users[str(user.id)]['level']
        xp_amt = users[str(user.id)]['experience']
        level_up_point = int(1000 * (1.15 ** (profile[1]-1)))

        em = discord.Embed(title = f"{member}'s profile", color = discord.Color.red())
    
        em.add_field(name = 'Level', value = lvl_amt, inline=False)
        em.add_field(name = 'Experience', value = f'{xp_amt}/{level_up_point}', inline=False)
        await ctx.send(embed = em)

    #XP command
    @commands.Cog.listener()
    async def on_message(self, ctx):
        await open_profile(ctx.author)
        users = await get_profile_data()
        user = ctx.author

        profile = await update_profile(ctx.author)

        level_up_point = int(1000 * (1.15 ** (profile[1]-1)))

        xp_gain = random.randint(50, 100)
        print(f"{ctx.author.mention}: You earned {xp_gain}XP.")
    
        users[str(user.id)]['experience'] += xp_gain

        if profile[0] > level_up_point:
            users[str(user.id)]['level'] += 1
            users[str(user.id)]['experience'] -= level_up_point

        with open('user_profile.json', 'w') as f:
            json.dump(users, f)
        return True

#Opens the .json file
async def open_profile(user):
    users = await get_profile_data()

    #Places data in .json file if player is new
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['experience'] = 0
        users[str(user.id)]['level'] = 1

    with open('user_profile.json', 'w') as f:
        json.dump(users, f)
    return True

#Reads bank data from .json file
async def get_profile_data():
    with open('user_profile.json','r') as f:
        users = json.load(f)

    return users

#Updates bank data in the .json file
async def update_profile(user, change=0, mode='experience'):
    users = await get_profile_data()

    with open('user_profile.json', 'w') as f:
        json.dump(users, f)

    #List of all commodities
    profile =  [users[str(user.id)]['experience'], 
                users[str(user.id)]['level']]
            
    return profile

def setup(client):
    client.add_cog(Profile(client))
