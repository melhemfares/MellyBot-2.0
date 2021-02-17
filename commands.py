# -------- FUN COMMANDS --------

import discord
from discord.ext import commands
import random

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    #8Ball command
    @commands.command(aliases=['8ball'], help="Ask the Magic 8-Ball a question")
    async def _8ball(self, ctx, *, question):
        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                     "Don’t count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.", "My sources say no.",
                     "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.",
                     "Yes.", "Yes – definitely.", "You may rely on it."]

        answer = random.choice(responses)

        em = discord.Embed(title = f"Magic 8-Ball", color = discord.Color.blue())
                        
        em.add_field(name = f'{ctx.author}\'s question', value = f'```{question}```', inline = False)
        em.add_field(name = '8-Ball says...', value = f'```{answer}```', inline = False)
        await ctx.send(embed = em)

    #Blessed command
    @commands.command(help="See how blessed you are")
    async def blessed(self, ctx):
        blessed = random.randint(0,100)
        after_message = ''
    
        if blessed == 100:
            after_message = 'You are perfection! :money_mouth:'
        elif blessed > 90:
            after_message = 'You are hella blessed!'
        elif blessed > 80:
            after_message = 'You are exceptionally blessed!'
        elif blessed > 70:
            after_message = 'You are quite blessed!'
        elif blessed > 60:
            after_message = 'You are fairly blessed.'
        elif blessed > 60:
            after_message = 'You are alright.'
        elif blessed > 50:
            after_message = 'You are meh.'
        elif blessed > 40:
            after_message = 'You are a bit broke ngl.'
        elif blessed > 30:
            after_message = 'You are a kinda mosh up.'
        elif blessed > 20:
            after_message = 'You are quite mod.'
        elif blessed > 10:
            after_message = 'You are sooooo beg.'
        else:
            after_message = 'You are the ultimate begness'

        await ctx.send(f'{ctx.author.mention}: You scored {blessed}% blessed. {after_message}')

    #Lunchbox command
    @commands.command(help="See what's inside Melly's lunchbox")
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
        random_item = random.choice(lb_items)
        await ctx.send('Oh Mellyyy, what\'s in the lunchbox?')
        await ctx.send(random_item)

    #Melly command
    @commands.command(help="Sends 'Melly' with a random amount of y's at the end.")
    async def melly(self, ctx):
        melly = 'Mell'
        melly_suffix = ''

        y_amount = random.randint(1, 20)
        y = 'y' * y_amount

        if y_amount == 20:
            melly_suffix = '!!!!'
        elif y_amount >= 15:
            melly_suffix = '!!!'
        elif y_amount >= 10:
            melly_suffix = '!!'
        elif y_amount >= 2:
            melly_suffix = '!'
        else:
            melly_suffix = '...'

        await ctx.send(f'{melly}{y}{melly_suffix}')

def setup(client):
    client.add_cog(Fun(client))
