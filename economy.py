# -------- ECONOMY COMMANDS --------

import discord
from discord.ext import commands
import json
import os
import random
import asyncio
import requests
import time
from quickchart import QuickChart
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies

stocks_up = True
bot_startup = int(time.time())
STOCK_API = os.environ["STOCK_API"]

try:
    ts = TimeSeries(STOCK_API, output_format='pandas')
    crypto = CryptoCurrencies(STOCK_API, output_format='pandas')

    mlly, columns = ts.get_daily(symbol='AAPL')
    bngr, columns = ts.get_daily(symbol='TSLA')
    ytl, columns = ts.get_daily(symbol='LYFT')
    clyn, columns = ts.get_daily(symbol='FB')

    btc, columns = crypto.get_digital_currency_daily(symbol='BTC', market='CAD')

except:
    stocks_up = False
    print('Stock API reached its limit, wait a minute and try again (5 calls/minute, 500 calls/day)')

os.chdir('C:\\Users\\fares\\Desktop\\Discord Bots\\MellyBot 2.0\\cogs')

mainshop = [{'name':'MellyCoin','emoji':':coin:','price':10,'description':'Just a prop'},
            {'name':'Bomb','emoji':':bomb:','price':200,'description':'Clap someone up'},
            {'name':'Baby_Bottle','emoji':':baby_bottle:','price':1000,'description':'Increase time to answer math'},
            {'name':'Lebanese_Chicken','emoji':':poultry_leg:','price':1500,'description':'Buffs your grind results'},
            {'name':'Banana','emoji':':banana:','price':2500,'description':'Buffs your math prizes'},
            {'name':'Laptop','emoji':':computer:','price':10000,'description':'Allows you to buy stocks and use the Internet'}]

internet = [{'name':'Four_Leaf_Clover','emoji':':four_leaf_clover:','price':20000,'description':'Get luckier with mb.search'},
            {'name':'Bitcoin_ASIC','emoji':':pick:','price':25000,'description':'Allows you to mine bitcoin'},
            {'name':'Bomb_Shelter','emoji':':house:','price':30000,'description':'Protects you against bombs'},
            {'name':'Edmonds_Taxi','emoji':':oncoming_taxi:','price':100000,'description':'Slam into people and make them lose big money'}]

if stocks_up:
    stocks_list = [{'name':'MLLY','price':int(mlly['1. open'][0]),'description':'MellyCoin'},
                   {'name':'BNGR','price':int(bngr['1. open'][0]),'description':'Banger Inc.'},
                   {'name':'ZYRN','price':int(clyn['1. open'][0]),'description':'Zyrien Corp.'},
                   {'name':'YTL','price':int(ytl['1. open'][0]),'description':'YouTube Leb'}]

    bitcoin_price = int(btc['1a. open (CAD)'][0])

class Economy(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on a cooldown. Try again in `%.2fs` second(s)." % error.retry_after)
        raise error

    #Balance command
    @commands.command(aliases=['wallet', 'bank', 'bal'], help="Check your wallet, bank, and bitcoin amount.")
    async def balance(self, ctx, member:discord.Member=None):

        if member == None:
            member = ctx.author
            
        await open_account(member)
        user = member

        users = await get_bank_data()

        users[str(user.id)]['bitcoin'] = round(users[str(user.id)]['bitcoin'], 4)

        wallet_amt = users[str(user.id)]['wallet']
        bank_amt = users[str(user.id)]['bank']
        bitcoin_amt = users[str(user.id)]['bitcoin']

        wallet_amt_suffix = ''
        bank_amt_suffix = ''
        bitcoin_amt_suffix = ''

        #Wallet Amount display
        if wallet_amt >= 1000000000000:
            wallet_amt_suffix = 'tril'
            wallet_amt = round(wallet_amt/1000000000000, 3)
        elif wallet_amt >= 1000000000:
            wallet_amt_suffix = 'bil'
            wallet_amt = round(wallet_amt/1000000000, 3)
        elif wallet_amt >= 1000000:
            wallet_amt_suffix = 'mil'
            wallet_amt = round(wallet_amt/1000000, 3)
        else:
            wallet_amt_suffix = ''

        #Bank Amount display
        if bank_amt >= 1000000000000:
            bank_amt_suffix = 'tril'
            bank_amt = round(bank_amt/1000000000000, 3)
        elif bank_amt >= 1000000000:
            bank_amt_suffix = 'bil'
            bank_amt = round(bank_amt/1000000000, 3)
        elif bank_amt >= 1000000:
            bank_amt_suffix = 'mil'
            bank_amt = round(bank_amt/1000000, 3)
        else:
            bank_amt_suffix = ''

        #Bitcoin Amount display
        if bitcoin_amt >= 1000000000:
            bitcoin_amt_suffix = 'bil'
            bitcoin_amt = round(bitcoin_amt/1000000000, 3)
        elif wallet_amt >= 1000000:
            bitcoin_amt_suffix = 'mil'
            bitcoin_amt = round(bitcoin_amt/1000000, 3)
        else:
            bitcoin_amt_suffix = ''

        await open_account(member)
        em = discord.Embed(title = f"{member}'s balance", color = discord.Color.red())
    
        em.add_field(name = 'Wallet', value = f'{wallet_amt} {wallet_amt_suffix}')
        em.add_field(name = 'Bank', value = f'{bank_amt} {bank_amt_suffix}')
        em.add_field(name = 'Bitcoin', value = f'{bitcoin_amt} {bitcoin_amt_suffix}')
        await ctx.send(embed = em)

    #Test command
    @commands.command()
    async def test(self, ctx):
        current_time = int(time.time())
        time_passed = current_time - bot_startup
        await ctx.send(f"It's been {time_passed} seconds since this command was used.")

    #Bitcoin command
    @commands.command(aliases=['btc'], help="View bitcoin prices or sell your bitcoin.")
    async def bitcoin(self, ctx, mode=None, amount=None):

        if stocks_up:
            await open_account(ctx.author)
            user = ctx.author

            users = await get_bank_data()

            bal = await update_bank(ctx.author)

            if mode == None:
                await ctx.send(f'{ctx.author.mention}: You must specify if you want to view or sell')

            elif mode == 'view':
                if amount == None:
                    amount = '14'

                amount = int(amount)

                if amount < 0:
                    await ctx.send(f'{ctx.author.mention}: Only positive numbers allowed')
                elif amount > 100:
                    await ctx.send(f'{ctx.author.mention}: You cannot go past 100 days')
                else:
                    btc_prices = []
                    label_count = []

                    for i in range(amount, 0, -1):
                        label_count.append(str(btc.index.date[i]))
                        btc_prices.append(btc['1a. open (CAD)'][i])

                    qc = QuickChart()
                    qc.width = 500
                    qc.height = 300
                    qc.background_color = 'white'
                    qc.device_pixel_ratio = 2.0
                    qc.config = {
                        "type": "line",
                        "data": {
                            "labels": label_count,
                            "datasets": [{
                                "label": "BTC",
                                "data": btc_prices,
                                "fill": False,
                                "borderColor": 'orange'
                            }]
                        }
                    }

                    bitcoin_chart = qc.get_short_url()
                    
                    em = discord.Embed(title = f"Price of Bitcoin", color = discord.Color.orange())
                            
                    em.set_image(url=bitcoin_chart)
                    em.add_field(name = 'BTC', value = f'Prices for the last {amount} days', inline = False)
                    em.add_field(name = 'Current Price', value = '```%sMM```' %bitcoin_price, inline = False)
                    await ctx.send(embed = em)
            
            elif mode == 'sell':
                await open_account(ctx.author)

                if amount == None:
                    await ctx.send(f"{ctx.author.mention}: Please enter the amount")
                    return

                bal = await update_bank(ctx.author)
                if amount == 'all':
                    amount = bal[6]

                amount = float(amount)

                earnings = int(amount*bitcoin_price)

                if amount > bal[6]:
                    await ctx.send(f"{ctx.author.mention}: You don't have that much bitcoin")
                    return
                if amount < 0:
                    await ctx.send(f"{ctx.author.mention}: You must enter a positive number")
                    return

                await ctx.send(f"{ctx.author.mention}: You sold {amount} bitcoin and earned {earnings}MM")

                await update_bank(ctx.author, -1*amount, 'bitcoin')
                await update_bank(ctx.author, earnings, 'bank')
                    
            else:
                await ctx.send(f'{ctx.author.mention}: That option doesn\'t exist')
        else:
            await ctx.send('Stock API is down for now. Reload in a minute and try again.')

    #Buy command
    @commands.command(help="Buy an item from the main shop")
    async def buy(self, ctx, item, amount='1'):
        await open_account(ctx.author)

        res = await buy_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send(f'{ctx.author.mention}: That item doesn\'t exist')
                return
            if res[1] == 2:
                await ctx.send(f'{ctx.author.mention}: You don\'t have enough money in your wallet to buy that')
                return
            
        if res[2] == 1:
            await ctx.send(f'{ctx.author.mention}: You just bought {res[2]} {item}')
        else:
            await ctx.send(f'{ctx.author.mention}: You just bought {res[2]} {item}s')

    #Deposit command
    @commands.command(help="Deposit money from your wallet to the bank.")
    async def deposit(self, ctx, amount = None):
        await open_account(ctx.author)

        if amount == None:
            await ctx.send(f"{ctx.author.mention}: Please enter the amount")
            return

        bal = await update_bank(ctx.author)
        if amount == 'all':
            amount = bal[0]

        amount = int(amount)

        if amount > bal[0]:
            await ctx.send(f"{ctx.author.mention}: You don't have that much money")
            return
        if amount < 0:
            await ctx.send(f"{ctx.author.mention}: You must enter a positive number")
            return

        await update_bank(ctx.author, -1*amount)
        await update_bank(ctx.author, amount, 'bank')

        await ctx.send(f"{ctx.author.mention}: You deposited {amount}MM to the bank")

    #Gamble command
    @commands.command(help="Try your luck with a 50/50 gamble to double your money.")
    async def gamble(self, ctx, amount = None):
        await open_account(ctx.author)

        if amount == None:
            await ctx.send(f"{ctx.author.mention}: Please enter the amount")
            return

        bal = await update_bank(ctx.author)
        if amount == 'all':
            amount = bal[0]

        amount = int(amount)

        if amount > bal[0]:
            await ctx.send(f"{ctx.author.mention}: You don't have that much money")
            return
        if amount < 0:
            await ctx.send(f"{ctx.author.mention}: You must enter a positive number")
            return

        lucky = random.randint(1,2)
        await update_bank(ctx.author, -1*amount)

        if lucky == 1:
            await update_bank(ctx.author, 2*amount)
            await ctx.send(f"{ctx.author.mention}: Congrats! You won {amount*2}MM!")
        else:
            await ctx.send(f"{ctx.author.mention}: It's over. You lost the gamble")

    #Grind command
    @commands.command(help="Grind for Melly Money")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def grind(self, ctx):
        await open_account(ctx.author)
        users = await get_bank_data()
        user = ctx.author

        bal = await update_bank(ctx.author)

        lucky = random.randint(1,10)

        if lucky != 10:
            earnings = int(random.randint(50, 100) * bal[2])
            await ctx.send(f"{ctx.author.mention}: You grinded for that bread. You earned {earnings}MM!")
        else:
            earnings = int(random.randint(100, 200) * bal[2])
            await ctx.send(f"{ctx.author.mention}: You grinded extra hard for that bread. You earned {earnings}MM!")

        users[str(user.id)]['wallet'] += earnings

        with open('user_data.json', 'w') as f:
            json.dump(users, f)
        return True

    #Internet command
    @commands.command(help="Access the Internet (laptop required)")
    async def internet(self, ctx, mode=None, item=None, amount='1'):
        
        await open_account(ctx.author)
        user = ctx.author

        users = await get_bank_data()

        bal = await update_bank(ctx.author)

        #Check if user has laptop
        if bal[5] == False:
            await ctx.send(f'{ctx.author.mention}: You must own a laptop to access the Internet.')
        else:
            #mb.internet
            if mode == None:
                em = discord.Embed(title='TOR Browser')

                for item in internet:
                    name = item['name']
                    emoji = item['emoji']
                    price = item['price']
                    desc = item['description']
                    em.add_field(name = f'{name} {emoji}', value = f'{desc} ```{price}MM```')

                await ctx.send(embed=em)
                await ctx.send('You can also do mb.internet buy.')

            #mb.internet buy
            elif mode == 'buy':
                #Check if user specified an item
                if item == None:
                    await ctx.send(f'{ctx.author.mention}: You must specify which item you want to buy')
                else:
                    await open_account(ctx.author)

                    res = await buy_this_ii(ctx.author, item, amount)

                    if not res[0]:
                        if res[1] == 1:
                            await ctx.send(f'{ctx.author.mention}: That item doesn\'t exist')
                            return
                        if res[1] == 2:
                            await ctx.send(f'{ctx.author.mention}: You don\'t have enough money in your bank to buy that')
                            return

                    amount = res[2]
                    amount = int(amount)
                        
                    if amount == 1:
                        await ctx.send(f'{ctx.author.mention}: You just bought {amount} {item}')
                    else:
                        await ctx.send(f'{ctx.author.mention}: You just bought {amount} {item}s')

                    if item == 'bitcoin_asic':
                        await open_account(ctx.author)
                        users = await get_bank_data()
                        user = ctx.author

                        users[str(user.id)]['asic'] += 1 * amount

                        if bal[7] < 1:
                            await ctx.send(f'Congrats! You can now mine bitcoin using mb.mine.')
                        else:
                            await ctx.send(f'Mining power increased to {bal[7] + (1 * amount)}!')

                        with open('user_data.json', 'w') as f:
                            json.dump(users, f)
                        return True

                    if item == 'edmonds_taxi':
                        await open_account(ctx.author)
                        users = await get_bank_data()
                        user = ctx.author

                        users[str(user.id)]['taxi'] = True

                        await ctx.send(f'{ctx.author.mention}: You can now slam people with mb.slam [user]')

                        with open('user_data.json', 'w') as f:
                            json.dump(users, f)
                        return True

                    if item == 'bomb_shelter':
                        await open_account(ctx.author)
                        users = await get_bank_data()
                        user = ctx.author

                        users[str(user.id)]['bomb_shelter'] = True

                        await ctx.send(f'{ctx.author.mention}: You are now protected from all bombs.')

                        with open('user_data.json', 'w') as f:
                            json.dump(users, f)
                        return True
            else:
                await ctx.send('An error has occured. Try again.')
    
    #Inventory command
    @commands.command(aliases=['bag', 'inven'], help="Check your inventory.")
    async def inventory(self, ctx):
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()

        try:
            bag = users[str(user.id)]['bag']
        except:
            bag = []

        em = discord.Embed(title = "Inventory")
        for item in bag:
            name = item['item']
            amount = item['amount']

            em.add_field(name = name, value = amount)

        await ctx.send(embed = em)

    #Leaderboard command
    @commands.command(aliases = ['lb'], help="Check the leaderboard to see who's the richest.")
    async def leaderboard(self, ctx, x = 3):
        users = await get_bank_data()
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            total_amount = users[user]["wallet"] + users[user]["bank"]
            leader_board[total_amount] = name
            total.append(total_amount)

        total = sorted(total,reverse=True)    

        em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0xfa43ee))
        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = self.client.get_user(id_)
            name = member.name
            em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
            if index == x:
                break
            else:
                index += 1

        await ctx.send(embed = em)

    #Math command
    @commands.command(help="Solve a simple math problem to earn Melly Money.")
    async def math(self, ctx):
        await open_account(ctx.author)
        bal = await update_bank(ctx.author)
        
        num1 = random.randint(1, 12)
        num2 = random.randint(1, 12)
        num3 = random.randint(1, 20)

        answer = num1 * num2 + num3
        earnings = int(answer * bal[3])
        answer = str(answer)

        time = 10 + bal[4]

        await ctx.send(f'{ctx.author.mention}: What is {num1} * {num2} + {num3}? {time} seconds, go!')

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            msg = await self.client.wait_for('message', check=check, timeout=time)
            if msg.content.lower() == answer:

                await open_account(ctx.author)
                users = await get_bank_data()
                user = ctx.author
                users[str(user.id)]['wallet'] += earnings

                await ctx.send(f'{ctx.author.mention}: Correct! You earned {earnings}MM')

                with open('user_data.json', 'w') as f:
                    json.dump(users, f)
                return True
            else:
                await ctx.send(f'{ctx.author.mention}: Wrong, you monkey! The answer was {answer}')
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention}: You ran out of time. The answer was {answer}')
            
    #Mine command
    @commands.command(help="Mine for bitcoin (laptop and bitcoin ASIC required)")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def mine(self, ctx):
        await open_account(ctx.author)
        users = await get_bank_data()
        user = ctx.author

        bal = await update_bank(ctx.author)

        if bal[5]:
            if bal[7] > 0:
                lucky = random.randint(1,10)

                await ctx.send(":coin: :pick:")

                if lucky != 10:
                    earnings = round((random.randint(2000, 3000) / bitcoin_price) * bal[7], 4)
                    await ctx.send(f"{ctx.author.mention}: Your ASIC mined away. You earned {earnings} bitcoin!")
                else:
                    earnings = round((random.randint(3000, 5000) / bitcoin_price) * bal[7], 4)
                    await ctx.send(f"{ctx.author.mention}: Your ASIC mined barrreeee. You earned {earnings} bitcoin!")

                users[str(user.id)]['bitcoin'] += earnings

                with open('user_data.json', 'w') as f:
                    json.dump(users, f)
                return True
            
            else:
                await ctx.send(f'{ctx.author.mention}: You cannot mine without a bitcoin ASIC')
        else:
            await ctx.send(f'{ctx.author.mention}: You cannot mine without a laptop')

    #Search command
    @commands.command(help="Search Value Village for goodies")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def search(self, ctx):
        await open_account(ctx.author)
        users = await get_bank_data()
        user = ctx.author

        bal = await update_bank(ctx.author)

        lucky = random.randint(1,100)
        earnings = 0

        if lucky == 100:
            earnings = 3300
            await ctx.send(f"{ctx.author.mention}: You searched Value Village and found a gold chain! {earnings}MM for you.")
        elif lucky >= 80:
            earnings = int(random.randint(250, 300))
            await ctx.send(f"{ctx.author.mention}: You searched Value Village and found some silver! {earnings}MM for you.")
        elif lucky >= 60:
            earnings = int(random.randint(200, 250))
            await ctx.send(f"{ctx.author.mention}: You searched Value Village and found a boom box! {earnings}MM for you.")
        elif lucky >= 40:
            earnings = int(random.randint(100, 200))
            await ctx.send(f"{ctx.author.mention}: You searched Value Village and found some fresh shoes! {earnings}MM for you.")
        elif lucky >= 20:
            earnings = int(random.randint(100, 200) * -1)
            await ctx.send(f"{ctx.author.mention}: You searched Value Village and got boxed for cutting in line. {earnings}MM...")
        else:
            await ctx.send(f"{ctx.author.mention}: You searched Value Village and found nothing good.")

        users[str(user.id)]['wallet'] += earnings

        if bal[0] < 0:
            users[str(user.id)]['wallet'] = 0

        with open('user_data.json', 'w') as f:
            json.dump(users, f)
        return True
    
    #Send command
    @commands.command(aliases=['give'], help="Send money from the bank to another user")
    async def send(self, ctx, member:discord.Member, amount = None):
        await open_account(ctx.author)
        await open_account(member)

        if amount == None:
            await ctx.send(f"{ctx.author.mention}: Please enter the amount")
            return

        bal = await update_bank(ctx.author)
        if amount == 'all':
            amount = bal[1]

        amount = int(amount)

        if amount > bal[1]:
            await ctx.send(f"{ctx.author.mention}: You don't have that much money")
            return
        if amount < 0:
            await ctx.send(f"{ctx.author.mention}: You must enter a positive number")
            return

        await update_bank(ctx.author, -1*amount, 'bank')
        await update_bank(member, amount, 'bank')

        await ctx.send(f"{ctx.author.mention}: You gave {amount}MM to {member}")

    #Shop command
    @commands.command(help="View the main shop")
    async def shop(self, ctx):
        em = discord.Embed(title='Shop')

        for item in mainshop:
            name = item['name']
            emoji = item['emoji']
            price = item['price']
            desc = item['description']
            em.add_field(name = f'{name} {emoji}', value = f'{price}MM | {desc}')

        await ctx.send(embed=em)

    #Slam command
    @commands.command(help="Slam into another user (taxi required)")
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def slam(self, ctx, member:discord.Member=None):
        await open_account(ctx.author)
        user = ctx.author

        users = await get_bank_data()

        bal = await update_bank(ctx.author)

        if bal[8]:
            if member == None:
                await ctx.send(f'{ctx.author.mention}: You must target someone to use the taxi.')
            else:
                await open_account(member)
                users = await get_bank_data()
                user = member

                bal = await update_bank(user)

                losses = random.randint(2500, 5000)
            
                await update_bank(member, losses*-1)

                await ctx.send(':boom: :taxi:')
                await ctx.send(f'{member.mention} you got slammed into by {ctx.author.mention} and lost {losses}MM. Take that!.')

                if bal[0] < losses:
                    users[str(user.id)]['wallet'] = 0

                with open('user_data.json', 'w') as f:
                    json.dump(users, f)
                return True
        else:
            await ctx.send(f'{ctx.author.mention}: You do not own a taxi.')

    #Stats command
    @commands.command(aliases=['stats'], help="Check yours or another user's stats.")
    async def statisics(self, ctx, member:discord.Member=None):

        if member == None:
            member = ctx.author
            
        await open_account(member)
        user = member

        users = await get_bank_data()

        grind_amt = users[str(user.id)]['grind']
        math_amt = users[str(user.id)]['math']
        cooldown_amt = users[str(user.id)]['time']
        laptop_amt = users[str(user.id)]['laptop']
        bomb_shelter_amt = users[str(user.id)]['bomb_shelter']
        taxi_amt = users[str(user.id)]['taxi']
        asic_amt = users[str(user.id)]['asic']
        
        await open_account(member)
        em = discord.Embed(title = f"{member}'s stats", color = discord.Color.blue())
    
        em.add_field(name = 'Grind Bonus', value = 'x%s' % grind_amt)
        em.add_field(name = 'Math Bonus', value = 'x%s' % math_amt)
        em.add_field(name = 'Math Time Bonus', value = '%s sec' % cooldown_amt)
        em.add_field(name = 'Owns Laptop?', value = '%s' % laptop_amt)
        em.add_field(name = 'Owns Bomb Shelter?', value = '%s' % bomb_shelter_amt)
        em.add_field(name = 'Owns Taxi?', value = '%s' % taxi_amt)
        em.add_field(name = 'Mining Power', value = '%sGHz' % asic_amt)

        await ctx.send(embed = em)

    #Stocks command
    @commands.command(help="Access the stock market (laptop required)")
    async def stocks(self, ctx, mode=None, stock=None, amount='0'):
        
        await open_account(ctx.author)
        user = ctx.author

        users = await get_bank_data()

        bal = await update_bank(ctx.author)

        if stocks_up:
            #Check if user has laptop
            if bal[5] == False:
                await ctx.send(f'{ctx.author.mention}: You must own a laptop to access the stock market.')
            else:
                #mb.stocks
                if mode == None:
                    em = discord.Embed(title='Stocks')

                    for stock in stocks_list:
                        name = stock['name']
                        price = stock['price']
                        desc = stock['description']
                        em.add_field(name = name, value = f'{desc} ```{price}MM```')

                    await ctx.send(embed=em)
                    await ctx.send('You can also do mb.stocks view, buy or sell.')

                #mb.stocks view
                elif mode == 'view':
                    await open_account(ctx.author)
                    user = ctx.author
                    users = await get_bank_data()

                    try:
                        stocks = users[str(user.id)]['stocks']
                    except:
                        stocks = []

                    em = discord.Embed(title = f"{ctx.author}'s Stock Portfolio")
                    for item in stocks:
                        name = item['stock']
                        amount = item['amount']

                        em.add_field(name = name, value = amount)

                    await ctx.send(embed = em)

                #mb.stocks buy
                elif mode == 'buy':
                    #Check if user specified a stock
                    if stock == None:
                        await ctx.send(f'{ctx.author.mention}: You must specify which stock you want to buy?')
                    else:
                        await open_account(ctx.author)

                        res = await buy_this_stock(ctx.author, stock, amount)

                        if not res[0]:
                            if res[1] == 1:
                                await ctx.send(f'{ctx.author.mention}: That stock doesn\'t exist')
                                return
                            if res[1] == 2:
                                await ctx.send(f'{ctx.author.mention}: You don\'t have enough money in your bank to buy that')
                                return
                            
                        amount = res[2]
                        amount = int(amount)

                        if amount == 1:
                            await ctx.send(f'{ctx.author.mention}: You just bought {amount} share in {stock}')
                        else:
                            await ctx.send(f'{ctx.author.mention}: You just bought {amount} shares in {stock}')

                #mb.stocks sell
                elif mode == 'sell':
                    await open_account(ctx.author)

                    res = await sell_this_stock(ctx.author, stock, amount)
                    bal = await update_bank(ctx.author)

                    if not res[0]:
                        if res[1] == 1:
                            await ctx.send(f'{ctx.author.mention}: That stock doesn\'t exist')
                            return
                        if res[1] == 2:
                            await ctx.send(f'{ctx.author.mention}: You don\'t have that much {stock}')
                            return
                        if res[1] == 3:
                            await ctx.send(f'You don\'t have any {stock}')
                            return

                    amount = res[2]
                    amount = int(amount)
                        
                    if amount == 1:
                        await ctx.send(f'{ctx.author.mention}: You just sold {amount} share in {stock}')
                    else:
                        await ctx.send(f'{ctx.author.mention}: You just sold {amount} shares in {stock}')

                else:
                    await ctx.send('An error has occured. Try again.')
        else:
            await ctx.send('Stock API is down for now. Reload in a minute and try again.')

    #Use command
    @commands.command(help="Use an item in your inventory")
    async def use(self, ctx, item, amount='1', member:discord.Member=None):
        await open_account(ctx.author)

        res = await use_this(ctx.author, item, amount)
        bal = await update_bank(ctx.author)

        if not res[0]:
            if res[1] == 1:
                await ctx.send(f'{ctx.author.mention}: That item doesn\'t exist')
                return
            if res[1] == 2:
                await ctx.send(f'{ctx.author.mention}: You don\'t have that many {item}s')
                return
            if res[1] == 3:
                await ctx.send(f'You don\'t have any {item}s in your inventory')
                return

        amount = res[2]
        amount = int(amount)    

        if amount == 1:
            await ctx.send(f'{ctx.author.mention}: You just used {amount} {item}')
        else:
            await ctx.send(f'{ctx.author.mention}: You just used {amount} {item}s')

        if item == 'bomb':

            if member == None:
                await ctx.send(f'{ctx.author.mention}: You must target someone to use the bomb')
            else:
                await open_account(member)
                users = await get_bank_data()
                user = member

                bal = await update_bank(user)

                losses = 0
                for x in range(amount):
                    losses_ = random.randint(150,300)
                    losses += losses_

                if bal[9]:
                    await ctx.send(f'{member.mention} you got bombed by {ctx.author.mention} but you were protected by your bomb shelter.')
                else:
                    await update_bank(member, losses*-1)

                await ctx.send(f'{member.mention} you got bombed by {ctx.author.mention} and lost {losses}MM. Kablam!.')

                if bal[0] < losses:
                    users[str(user.id)]['wallet'] = 0

                with open('user_data.json', 'w') as f:
                    json.dump(users, f)
                return True

        if item == 'lebanese_chicken':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['grind'] += 0.5 * amount

            await ctx.send(f'Grind bonus increased to x{bal[2] + (0.5 * amount)}!')

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

        if item == 'banana':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['math'] += 0.5 * amount

            await ctx.send(f'Math bonus increased to x{bal[3] + (0.5 * amount)}!')

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

        if item == 'baby_bottle':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['time'] += 1 * amount

            await ctx.send(f'Math time bonus increased to {bal[4] + (1 * amount)}sec!')

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

        if item == 'laptop':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['laptop'] = True

            await ctx.send(f'Congrats! You can now buy stocks using mb.stocks and use the Internet with mb.internet.')

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

    #Withdraw command
    @commands.command(help="Withdraw money from the bank")
    async def withdraw(self, ctx, amount = None):
        await open_account(ctx.author)

        if amount == None:
            await ctx.send(f"{ctx.author.mention}: Please enter the amount")
            return

        bal = await update_bank(ctx.author)
        if amount == 'all':
            amount = bal[1]

        amount = int(amount)

        if amount > bal[1]:
            await ctx.send(f"{ctx.author.mention}: You don't have that much money")
            return
        if amount < 0:
            await ctx.send(f"{ctx.author.mention}: You must enter a positive number")
            return

        await update_bank(ctx.author, amount)
        await update_bank(ctx.author, -1*amount, 'bank')

        await ctx.send(f"{ctx.author.mention}: You withdrew {amount}MM from the bank")

#Buy this function
async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    bal = await update_bank(user)

    if name_ == None:
        return [False, 1]

    if amount == 'max' or 'all':
        amount = int(bal[0] / price)

    amount = int(amount)

    cost = price*amount

    users = await get_bank_data()

    if bal[0] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['bag']:
            n = thing['item']
            if n == item_name:
                old_amt = thing['amount']
                new_amt = old_amt + amount
                users[str(user.ud)]['bag'][index]['amount'] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {'item':item_name, 'amount':amount}
            users[str(user.id)]['bag'].append(obj)
    except:
        obj = {'item':item_name, 'amount':amount}
        users[str(user.id)]['bag'] = [obj]

    with open('user_data.json','w') as f:
        json.dump(users, f)

    await update_bank(user, cost*-1, 'wallet')

    return [True, 'Worked', amount]

#Buy this function for Internet
async def buy_this_ii(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in internet:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    bal = await update_bank(user)

    if amount == 'max' or 'all':
        amount = int(bal[1] / price)

    amount = int(amount)

    cost = price*amount

    users = await get_bank_data()

    if bal[1] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['bag']:
            n = thing['item']
            if n == item_name:
                old_amt = thing['amount']
                new_amt = old_amt + amount
                users[str(user.ud)]['bag'][index]['amount'] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {'item':item_name, 'amount':amount}
            users[str(user.id)]['bag'].append(obj)
    except:
        obj = {'item':item_name, 'amount':amount}
        users[str(user.id)]['bag'] = [obj]

    with open('user_data.json','w') as f:
        json.dump(users, f)

    await update_bank(user, cost*-1, 'bank')

    return [True, 'Worked', amount]

#Buy this function for stocks
async def buy_this_stock(user, item_name, amount):
    item_name = item_name.upper()
    name_ = None
    for stocks in stocks_list:
        name = stocks["name"].upper()
        if name == item_name:
            name_ = name
            price = stocks["price"]
            break

    if name_ == None:
        return [False, 1]

    bal = await update_bank(user)

    if amount == 'max' or 'all':
        amount = int(bal[1] / price)

    amount = int(amount)

    cost = price*amount

    users = await get_bank_data()

    if bal[1] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['stocks']:
            n = thing['item']
            if n == item_name:
                old_amt = thing['amount']
                new_amt = old_amt + amount
                users[str(user.ud)]['stocks'][index]['amount'] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {'item':item_name, 'amount':amount}
            users[str(user.id)]['stocks'].append(obj)
    except:
        obj = {'stock':item_name, 'amount':amount}
        users[str(user.id)]['stocks'] = [obj]

    with open('user_data.json','w') as f:
        json.dump(users, f)

    await update_bank(user, cost*-1, 'bank')

    return [True, 'Worked', amount]

#Sell this function for stocks
async def sell_this_stock(user, item_name, amount, price = None):
    item_name = item_name.upper()
    name_ = None
    for stocks in stocks_list:
        name = stocks["name"].upper()
        if name == item_name:
            name_ = name
            if price==None:
                price = stocks["price"]
            break

    if name_ == None:
        return [False, 1]

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['stocks']:
            n = thing['stock']
            if n == item_name:
                if amount == 'max' or 'all':
                    amount = users[str(user.id)]['stocks'][index]['amount']
                    users[str(user.id)]['stocks'][index]['amount'] = 0
                    t = 1
                    break
                else:
                    amount = int(amount)
                    old_amt = thing['amount']
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False, 2]
                    users[str(user.id)]['stocks'][index]['amount'] = new_amt
                    t = 1
                    break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open('user_data.json','w') as f:
        json.dump(users, f)

    amount = int(amount)

    cost = price*amount

    await update_bank(user, cost, "bank")

    return [True, 'Worked', amount]

#Use this function to use mainshop items
async def use_this(user, item_name, amount, price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['bag']:
            n = thing['item']
            if n == item_name:
                if amount == 'max' or 'all':
                    amount = users[str(user.id)]['bag'][index]['amount']
                    t = 1
                    break
                else:
                    amount = int(amount)
                    old_amt = thing['amount']
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False, 2]
                    users[str(user.id)]['bag'][index]['amount'] = new_amt
                    t = 1
                    break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open('user_data.json','w') as f:
        json.dump(users, f)

    return [True, 'Worked', amount]
    
#Opens the .json file
async def open_account(user):
    users = await get_bank_data()

    #Places data in .json file if player is new
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 0
        users[str(user.id)]['grind'] = 1
        users[str(user.id)]['math'] = 1
        users[str(user.id)]['time'] = 0
        users[str(user.id)]['laptop'] = False
        users[str(user.id)]['bitcoin'] = 0.0000
        users[str(user.id)]['asic'] = 0
        users[str(user.id)]['taxi'] = False
        users[str(user.id)]['bomb_shelter'] = False

    with open('user_data.json', 'w') as f:
        json.dump(users, f)
    return True

#Reads bank data from .json file
async def get_bank_data():
    with open('user_data.json','r') as f:
        users = json.load(f)

    return users

#Update bank data in the .json file
async def update_bank(user, change=0, mode='wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('user_data.json', 'w') as f:
        json.dump(users, f)

    #List of all commodities
    bal =  [users[str(user.id)]['wallet'], 
            users[str(user.id)]['bank'],
            users[str(user.id)]['grind'],
            users[str(user.id)]['math'],
            users[str(user.id)]['time'],
            users[str(user.id)]['laptop'],
            users[str(user.id)]['bitcoin'],
            users[str(user.id)]['asic'],
            users[str(user.id)]['taxi'],
            users[str(user.id)]['bomb_shelter']]
            
    return bal

def setup(client):
    client.add_cog(Economy(client))
