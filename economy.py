import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries('74O5O3OU1C3RZMD3', output_format='pandas')

mlly, columns = ts.get_daily(symbol='AAPL')
bngr, columns = ts.get_daily(symbol='TSLA')
ytl, columns = ts.get_daily(symbol='LYFT')
clyn, columns = ts.get_daily(symbol='FB')

os.chdir('C:\\Users\\Celeste\\Desktop\\Discord Bots\\MellyBot 2.0\\cogs')

mainshop = [{'name':'MellyCoin','price':10,'description':'Just a prop'},
            {'name':'Bomb','price':200,'description':'Clap someone up'},
            {'name':'Baby_Bottle','price':1000,'description':'Increase time to answer math'},
            {'name':'Lebanese_Chicken','price':1500,'description':'Buffs your grind results'},
            {'name':'Banana','price':2500,'description':'Buffs your math prizes'},
            {'name':'Laptop','price':10000,'description':'Allows you to buy stocks and use the Internet'}]

internet = [{'name':'Four_Leaf_Clover','price':20000,'description':'Get luckier with mb.search'},
            {'name':'Bitcoin_AISC','price':25000,'description':'Allows you to mine bitcoin'},
            {'name':'Bomb_Shelter','price':30000,'description':'Protects you against bombs'}]

stocks_list = [{'name':'MLLY','price':int(mlly['1. open'][0]),'description':'MellyCoin'},
              {'name':'BNGR','price':int(bngr['1. open'][0]),'description':'Banger Inc.'},
              {'name':'CLYN','price':int(clyn['1. open'][0]),'description':'Cailyn Corp.'},
              {'name':'YTL','price':int(ytl['1. open'][0]),'description':'YouTube Leb'}]

class Economy(commands.Cog):

    def __init__(self, client):
        self.client = client

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on a cooldown. Try again in %.2fs second(s)." % error.retry_after)
        else:
            raise error

    #Balance command
    @commands.command(aliases=['wallet', 'bank', 'bal'])
    async def balance(self, ctx, member:discord.Member=None):

        if member == None:
            member = ctx.author
            
        await open_account(member)
        user = member

        users = await get_bank_data()

        wallet_amt = users[str(user.id)]['wallet']
        bank_amt = users[str(user.id)]['bank']

        await open_account(member)
        em = discord.Embed(title = f"{member}'s balance", color = discord.Color.red())
    
        em.add_field(name = 'Wallet', value = wallet_amt)
        em.add_field(name = 'Bank', value = bank_amt)
        await ctx.send(embed = em)

    #Stats command
    @commands.command()
    async def stocks(self, ctx, mode=None, stock=None, amount=0):
        
        await open_account(ctx.author)
        user = ctx.author

        users = await get_bank_data()

        bal = await update_bank(ctx.author)

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
                    name = item['item']
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
                    
                if amount == 1:
                    await ctx.send(f'{ctx.author.mention}: You just sold {amount} share in {stock}')
                else:
                    await ctx.send(f'{ctx.author.mention}: You just sold {amount} shares in {stock}')

            else:
                await ctx.send('An error has occured. Try again.')

    #Mine command
    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def mine(self, ctx):
        await open_account(ctx.author)
        users = await get_bank_data()
        user = ctx.author

        bal = await update_bank(ctx.author)

        if bal[6] > 0:
            lucky = random.randint(1,10)

        if lucky != 10:
            earnings = int(random.randint(0.03, 0.05))
            await ctx.send(f"{ctx.author.mention}: Your ASIC mined for that bitcoin. You earned {earnings}MM!")
        else:
            earnings = int(random.randint(0.05, 0.1))
            await ctx.send(f"{ctx.author.mention}: Your ASIC mined barrreeee bitcoin. You earned {earnings}MM!")

        users[str(user.id)]['bitcoin'] += earnings

        with open('user_data.json', 'w') as f:
            json.dump(users, f)
        return True
    #Internet command
    @commands.command()
    async def internet(self, ctx, mode=None, item=None, amount=1):
        
        await open_account(ctx.author)
        user = ctx.author

        users = await get_bank_data()

        bal = await update_bank(ctx.author)

        #Check if user has laptop
        if bal[5] == False:
            await ctx.send(f'{ctx.author.mention}: You must own a laptop to access the stock market.')
        else:
            #mb.stocks
            if mode == None:
                em = discord.Embed(title='TOR Browser')

                for item in internet:
                    name = item['name']
                    price = item['price']
                    desc = item['description']
                    em.add_field(name = name, value = f'{desc} ```{price}MM```')

                await ctx.send(embed=em)
                await ctx.send('You can also do mb.internet buy.')

            #mb.stocks buy
            elif mode == 'buy':
                #Check if user specified a stock
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
                        
                    if amount == 1:
                        await ctx.send(f'{ctx.author.mention}: You just bought {amount} {item}')
                    else:
                        await ctx.send(f'{ctx.author.mention}: You just bought {amount} {item}s')
            else:
                await ctx.send('An error has occured. Try again.')

    #Stats command
    @commands.command(aliases=['profile', 'stats'])
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

        await open_account(member)
        em = discord.Embed(title = f"{member}'s stats", color = discord.Color.blue())
    
        em.add_field(name = 'Grind Bonus', value = 'x%s' % grind_amt, inline = False)
        em.add_field(name = 'Math Bonus', value = 'x%s' % math_amt, inline = False)
        em.add_field(name = 'Math Time Bonus', value = '%s sec' % cooldown_amt, inline = False)
        em.add_field(name = 'Owns Laptop?', value = '%s' % laptop_amt, inline = False)
        await ctx.send(embed = em)

    #Grind command
    @commands.command()
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

    #Grind command
    @commands.command()
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

    #Withdraw command
    @commands.command()
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

    #Deposit command
    @commands.command()
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
    
    #Send command
    @commands.command(aliases=['give'])
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

    #Math command
    @commands.command()
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

    #Gamble command
    @commands.command()
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

    #Shop command
    @commands.command()
    async def shop(self, ctx):
        em = discord.Embed(title='Shop')

        for item in mainshop:
            name = item['name']
            price = item['price']
            desc = item['description']
            em.add_field(name = name, value = f'{price}MM | {desc}')

        await ctx.send(embed=em)

    #Leaderboard command
    @commands.command(aliases = ['lb'])
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

    #Buy command
    @commands.command()
    async def buy(self, ctx, item, amount=1):
        await open_account(ctx.author)

        res = await buy_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send(f'{ctx.author.mention}: That item doesn\'t exist')
                return
            if res[1] == 2:
                await ctx.send(f'{ctx.author.mention}: You don\'t have enough money in your wallet to buy that')
                return
            
        if amount == 1:
            await ctx.send(f'{ctx.author.mention}: You just bought {amount} {item}')
        else:
            await ctx.send(f'{ctx.author.mention}: You just bought {amount} {item}s')

    #Use command
    @commands.command()
    async def use(self, ctx, item, member:discord.Member=None, amount=1,):
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

                await update_bank(member, losses*-1)

                await ctx.send(f'{member.mention} you got bombed by {ctx.author.mention} and lost {losses}MM. Take that you capitalist.')

        if item == 'lebanese_chicken':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['grind'] += 0.5

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

            await ctx.send(f'Grind bonus increased to x{bal[2]}!')

        if item == 'banana':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['math'] += 0.5

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

            await ctx.send(f'Math bonus increased to x{bal[3]}!')

        if item == 'baby_bottle':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['time'] += 1

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

            await ctx.send(f'Math time bonus {bal[4]}sec!')

        if item == 'laptop':
            await open_account(ctx.author)
            users = await get_bank_data()
            user = ctx.author

            users[str(user.id)]['laptop'] = True

            with open('user_data.json', 'w') as f:
                json.dump(users, f)
            return True

            await ctx.send(f'Congrats! You can now buy stocks using mb.stocks.')
       
    @commands.command(aliases=['bag'])
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

async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

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

    return [True, 'Worked']

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

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

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

    return [True, 'Worked']

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

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

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
        obj = {'item':item_name, 'amount':amount}
        users[str(user.id)]['stocks'] = [obj]

    with open('user_data.json','w') as f:
        json.dump(users, f)

    await update_bank(user, cost*-1, 'bank')

    return [True, 'Worked']

#Sell stocks
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

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['stocks']:
            n = thing['item']
            if n == item_name:
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

    await update_bank(user, cost, "bank")

    return [True, 'Worked']

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

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]['bag']:
            n = thing['item']
            if n == item_name:
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

    return [True, 'Worked']
    
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
        users[str(user.id)]['bitcoin'] = 0.0

    with open('user_data.json', 'w') as f:
        json.dump(users, f)
    return True

#Reads bank data from .json file
async def get_bank_data():
    with open('user_data.json','r') as f:
        users = json.load(f)

    return users

#Updates bank data in the .json file
async def update_bank(user, change=0, mode='wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('user_data.json', 'w') as f:
        json.dump(users, f)

    bal =   [users[str(user.id)]['wallet'], 
            users[str(user.id)]['bank'],
            users[str(user.id)]['grind'],
            users[str(user.id)]['math'],
            users[str(user.id)]['time'],
            users[str(user.id)]['laptop'],
            users[str(user.id)]['bitcoin']]
            
    return bal

def setup(client):
    client.add_cog(Economy(client))