import os, sys, json, discord, random, datetime, math, asyncio, time
from discord.ext import commands
from discord.ext.commands import *

with open("database/baseitems.json") as f: baseitems = json.load(f)
###weapons
#key: item name
#0: damage
#1: strength
#2: intelligence
#3: crit chance
#4: crit damage
#5: requirement
#6: price
#7: ability base dmg
###armor
#key: set name
#0: strength
#1: intelligence
#2: crit chance
#3: crit damage
#4: health
#5: defence
#6: price
###pets
#0: strength
#1: crit damage
#2: intelligence
#3: ability damage
#4: health
#5: defense
#6: price
with open("database/userdb.json") as f: userdb = json.load(f)
#key: user id
#0: coins
#1: coins bank
#2: selected class
#3: catacombs level, xp
#4: mage level, xp
#5: archer level, xp
#6: berserk level, xp
#7: tank level, xp
#8: mage armor, weapon, pet
#9: archer armor, weapon, pet
#10: berserk armor, weapon, pet
#11: tank armor, weapon, pet
#12: highest floor completion
with open("database/inventory.json") as f: inventory = json.load(f)
#key: user id
#0-9: inventory slot
with open("database/grind.json") as f: grind = json.load(f)
#key: user id
#0: unclaimed coins
#1: level
#2: enabled
with open("database/auctions.json") as f: auctions = json.load(f)
#key: auction id
#0: item
#1: price
#2: auction end time
#3: author

bosses = {
    "1": ["Bozo", "500k", "tiny", "*Involved in the dark arts due to his parents' insistence. Originally worked as a Circus Clown.*"],
    "2": ["Scarf", "1M", "small", "*First of his class. His teacher said he will do \"great things\".*"],
    "3": ["The Professor", "3M", "small", "*Despite his great technique, he failed the Masters exam three times. Works from 8 to 5. Cares about his students.*"],
    "4": ["Thorn", "300k (can be only damaged with spirit bow, 4 hits required)", "small", "*Powerful Necromancer who specializes in animals. Calls himself a vegetarian, go figure.*"],
    "5": ["Livid", "7M", "medium", "*Strongly believes he will become the Lord one day. Subject of mockeries, even from his disciples.*"],
    "6": ["Sadan", "40M", "medium", "*Necromancy was always strong in his family. Says he once beat a Wither in a duel. Likes to brag.*"],
    "7": ["Necron", "1B", "large", "*Disciples of the Wither King. Inherited the Catacombs eons ago. Never defeated, feared by anything living AND dead.*"]
}

class dungeon(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    def calculateDamage(self, basedmg:int, strength:int, cd:int):
        v1 = 5 + basedmg
        v2 = strength / 5
        v3 = v1 + v2
        v4 = 1 + strength/100
        v5 = v3*v4
        v6 = 1 + cd/100
        return v5*v6 #i dont trust python's order of operations

    def calculateEffectiveHealth(self, hp:int, defense:int):
        v1 = 1 + defense/100
        return hp*v1

    def calculateAbilityDamage(self, basedmg:int, mana:int, admg:int):
        v1 = 1 + mana/100
        v2 = basedmg*v1
        return v2*(1 + admg/100)

    def calculateSurvivalChances(self, floor:int, ehp:int):
        if floor == 1: return ehp/500 if ehp/500 < 100 else 100
        elif floor == 2: return ehp/1000 if ehp/1000 < 100 else 100
        elif floor == 3: return ehp/1500 if ehp/1500 < 100 else 100
        elif floor == 4: return ehp/3000 if ehp/3000 < 100 else 100
        elif floor == 5: return ehp/3500 if ehp/3500 < 100 else 100
        elif floor == 6: return ehp/3500 if ehp/3000 < 100 else 100
        elif floor == 7: return ehp/10000 if ehp/5000 < 100 else 100

    def calculateDungeonTime(self, floor:int, damage:int): return int((floor+3)*round(10/(math.log(damage+1, 10)+1), 0))

    def applyClassPositives(self, userid:int, damage:int):
        if userdb[str(userid)][2] == "berserk":
            c = 40
            for i in range(userdb[str(user.id)][7][0]): c += 1
            return damage*(1 + c/100)
        elif userdb[str(user.id)][2] == "archer":
            c = 100
            for i in range(userdb[str(user.id)][5][0]): c += 2
            return damage*(1 + c/100)

    def calculateTotalStats(self, userid:int):
        classes = ["mage", "archer", "berserk", "tank"]
        strength = 1 + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][0] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][1] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][0]
        intelligence = 100 + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][1] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][2] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][3]
        cd = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][4] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][4] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][1]
        cc = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][3] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][3] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][2]
        admg = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][4]
        hp = 100 +  baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][4] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][5]
        defense = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][5] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][6]
        if userdb[str(userid)][2] == "mage":
            for i in range(userdb[str(userid)][4][0]): intelligence += 20
        if userdb[str(userid)][2] == "tank":
            q = 20
            for i in range(userdb[str(userid)][6][0]): q += 1
            defense *= 1 + q/100
        if str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2]) == "sheep": intelligence *= 1.25
        if str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2]) == "blue whale":
            hp *= 1.20
            defense += round(hp/20, 0)
        stats = [strength, intelligence, cd, cc, hp, defense, admg]
        if str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2]) == "ender dragon":
            arr = []
            for stat in stats: arr.append(round(stat*1.10, 0))
            stats = arr
            del arr
        c = 100
        for i in range(userdb[str(userid)][3][0]): c += 10
        arr = []
        for stat in stats: arr.append(int(round(stat*c/100, 0)))
        return arr

    async def q(self):
        while True:
            for user in grind:
                if grind[user][2]: grind[user][0] += grind[user][1]*(100000 if grind[user][1] < 5 else 500000 if grind[user][1] < 10 else 1000000)
            with open("database/grind.json", "w+") as f: json.dump(grind, f)
            await asyncio.sleep(3600)

    @commands.Cog.listener()
    async def on_ready(self): await self.q()

    @commands.command(name="dungeon")
    async def a(self, ctx, floor:int):
        classes = ["mage", "archer", "berserk", "tank"]
        if floor not in list(range(1,8)): raise BadArgument
        if userdb[str(ctx.author.id)][12] != floor-1 and not userdb[str(ctx.author.id)][12] == floor and not userdb[str(ctx.author.id)][12] >= floor: return await ctx.reply("You need to complete the previous floor first")
        stats = self.calculateTotalStats(ctx.author.id)
        if userdb[str(ctx.author.id)][2] == "mage": x = self.calculateAbilityDamage(baseitems[str(userdb[str(ctx.author.id)][8][1])][7], stats[1], stats[6])
        else: x = self.calculateDamage(baseitems[str(userdb[str(ctx.author.id)][11][1])][0], stats[0], stats[2])
        y = self.calculateDungeonTime(floor, x)
        z = self.calculateSurvivalChances(floor, self.calculateEffectiveHealth(stats[4], stats[5]))
        r = int(''.join(random.choices([str(100000*floor), str(1000000*floor), str(100000000*floor)], [100, 0.15*floor, 0.04*floor], k=1)))
        cxp = [random.randint(100, 500), random.randint(500, 1000), random.randint(1000, 3000), random.randint(3000, 7000), random.randint(7000, 20000), random.randint(20000, 50000), random.randint(50000, 100000)]
        clxp = round(cxp[floor-1]/1.5, 0)
        await ctx.reply(f"You entered the Catacombs Floor {floor}, come back in {y} minutes to check your rewards")
        if z >= 100: s = [True]
        else: s = random.choices([False, True], [100-z, z], k=1)
        if not s[0]:
            if ctx.author.id != 705462972415213588: await asyncio.sleep(20)
            await ctx.author.send(f"You died in the dungeon. You earned:\n+{cxp[floor-1]/10} catacombs experience\n+{clxp/10} {userdb[str(ctx.author.id)][2]} experience")
            a1 = cxp[floor-1]/10
            a2 = clxp/10
        else:
            if ctx.author.id != 705462972415213588: await asyncio.sleep(float(y*60))
            await ctx.author.send(f"You completed the dungeons floor {floor}. You earned:\n+{cxp[floor-1]} catacombs experience\n+{clxp/10} {userdb[str(ctx.author.id)][2]} experience\n+{r} coins")
            a1 = cxp[floor-1]
            a2 = clxp
        userdb[str(ctx.author.id)][0] += r
        xp = 0
        for i in range(userdb[str(ctx.author.id)][3][0]):
            j = 1
            if i % 10: j += 1
            xp += j*1000
        userdb[str(ctx.author.id)][3][1] += a1
        if userdb[str(ctx.author.id)][3][1] >= xp:
            userdb[str(ctx.author.id)][3][0] += 1
            userdb[str(ctx.author.id)][3][1] = 0
        userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][1] += a2
        clxp = 0
        for i in range(userdb[str(ctx.author.id)][3][0]):
            j = 1
            if i % 10: j += 1
            clxp += j*750
        if userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][1] >= clxp:
            userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][0] += 1
            userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][1] = 0
        if userdb[str(ctx.author.id)][12] == floor-1: userdb[str(ctx.author.id)][12] += 1
        with open("database/userdb.json", "w+") as f: json.dump(userdb, f)

    @commands.command(name="selectclass", aliases=["setclass", "class"])
    async def b(self, ctx, x:str):
        classes = ["mage", "archer", "berserk", "tank"]
        if x.lower() not in classes: raise BadArgument
        userdb[str(ctx.author.id)][2] = x.lower()
        with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
        return await ctx.reply(f"you changed your class to {x.lower()}")

    @commands.command(name="stats")
    async def c(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb:
            userdb[str(user.id)] = [100, 0, "berserk", [1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 0]
            with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
        stats = self.calculateTotalStats(user.id)
        if userdb[str(user.id)][2] == "mage": x = self.calculateAbilityDamage(baseitems[str(userdb[str(user.id)][8][1])][7], stats[1], stats[6])
        else: x = self.calculateDamage(baseitems[str(userdb[str(user.id)][11][1])][0], stats[0], stats[2])
        e = discord.Embed(title=f"{user}'s stats", description=f"Health: {stats[4]}\nDefense: {stats[5]}\nEffective health: {int(self.calculateEffectiveHealth(stats[4], stats[5]))}\nStrength: {stats[0]}\nCritical Damage: {stats[2]}\nIntelligence: {stats[1]}\nAbility Damage: {stats[6]}\nEstimated damage: {int(x)}", color=discord.Color.random())
        return await ctx.reply(embed=e)
    
    @commands.command(name="info")
    async def d(self, ctx, floor):
        if int(floor) not in list(range(1, 8)): raise BadArgument
        e = discord.Embed(title=f"floor {floor} info", description=f"Boss: {bosses[floor][0]}\nBoss health: {bosses[floor][1]}\nDungeon size: {bosses[floor][2]}\n\n{bosses[floor][3]}", color=discord.Color.random())
        return await ctx.reply(embed=e)

    @commands.command(name="level")
    async def e(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb: userdb[str(user.id)] = [0, 0, "berserk", [1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 0]
        embed = discord.Embed(title=f"{user}'s level info", description=f"Catacombs level: {userdb[str(user.id)][3][0]}\nMage level: {userdb[str(user.id)][4][0]}\nArcher level: {userdb[str(user.id)][5][0]}\nBerserk level: {userdb[str(user.id)][6][0]}\nTank level: {userdb[str(user.id)][7][0]}\nClass average: {round((userdb[str(user.id)][4][0]+userdb[str(user.id)][5][0]+userdb[str(user.id)][6][0]+userdb[str(user.id)][7][0])/4, 1)}", color=discord.Color.random())
        return await ctx.reply(embed=embed)
    
    @commands.command(name="inventory")
    async def f(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in inventory or len(inventory[str(user.id)]) == 0: e = discord.Embed(title=f"{user}'s inventory", description="This user has no items", color=discord.Color.random())
        else:
            x = str()
            for i in range(len(inventory[str(user.id)])): x += f"slot {i+1}: {inventory[str(user.id)][i]}\n"
            e = discord.Embed(title=f"{user}'s inventory", description=x, color=discord.Color.random())
        return await ctx.reply(embed=e)
    
    @commands.command(name="auction")
    async def g(self, ctx, action:str, item:str=None, price:int=None, t:int=None):
        if action == "create":
            if len(list(auctions.keys())) >= 10: return await ctx.reply("the auctions queue is full")
            i = len(list(auctions.keys()))
            if item == None: raise MissingRequiredArgument
            if price == None: raise MissingRequiredArgument
            if t == None: raise MissingRequiredArgument
            if item.lower() not in inventory[str(ctx.author.id)]: return await ctx.reply(f"You dont own this item")
            if t > 1440: return await ctx.reply(f"Time should not be more than 24 hours")
            if t < 5: return await ctx.reply(f"Time should not be less than 5 minutes")
            if price <= 0: raise BadArgument
            inventory[str(ctx.author.id)].remove(item.lower())
            auctions[str(i)] = [item.lower(), price, time.time()+(t*60), ctx.author.id]
            with open("database/auctions.json", "w+") as f: json.dump(auctions, f)
            with open("database/inventory.json", "w+") as f: json.dump(inventory, f)
            e = discord.Embed(title="You created an auction", description=f"Item: {item.lower()}\nPrice: {price}\nEnds on: <t:{int(time.time()+(t*60))}:d>", color=discord.Color.green())
            return await ctx.reply(embed=e)
        elif action == "cancel":
            if item == None: raise MissingRequiredArgument
            if item not in list(auctions.keys()): return await ctx.reply("Invalid auction id")
            if auctions[item][3] != ctx.author.id: return await ctx.reply("This isn't your auction")
            if len(inventory[str(ctx.author.id)]) == 10: return await ctx.reply("Your inventory is full")
            inventory[str(ctx.author.id)].append(auctions[item][0])
            del auctions[item]
            with open("database/auctions.json", "w+") as f: json.dump(auctions, f)
            with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
            with open("database/inventory.json", "w+") as f: json.dump(inventory, f)
            return await ctx.reply("You canceled your auction")
        elif action == "list":
            if len(list(auctions.keys())) == 0: return await ctx.reply("There are no auctions right now")
            x = str()
            for i in range(len(list(auctions.keys()))):
                if i+1 > len(list(auctions.keys())): break
                x += f"**{auctions[str(i)][0]}**\nPrice: {auctions[str(i)][1]}\nEnds on: <t:{int(auctions[str(i)][2])}:d>\nId: {i}\n\n"
            e = discord.Embed(title="auction list", description=x, color=discord.Color.random())
            return await ctx.reply(embed=e)
        elif action == "buy":
            if item == None: raise MissingRequiredArgument
            if item not in list(auctions.keys()): raise BadArgument
            if ctx.author.id == auctions[item][3]: return await ctx.reply("This is your own auction")
            if time.time() > auctions[item][2]: return await ctx.reply("This auction has expired")
            if userdb[str(ctx.author.id)][0] < auctions[item][1]: return await ctx.reply("You don't have enough coins to buy this item")
            userdb[str(ctx.author.id)][0] -= auctions[item][1]
            userdb[str(auctions[item][3])][0] += auctions[item][1]
            if str(ctx.author.id) not in inventory: inventory[str(ctx.author.id)] = list()
            inventory[str(ctx.author.id)].append(auctions[item][0])
            await ctx.reply(f"You bought a {auctions[item][0]} for {auctions[item][1]} coins")
            u = await self.client.fetch_user(auctions[item][3])
            await u.send(f"{ctx.author} bought your {auctions[item][0]} for {auctions[item][1]} coins")
            del auctions[item]
            with open("database/auctions.json", "w+") as f: json.dump(auctions, f)
            with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
            with open("database/inventory.json", "w+") as f: json.dump(inventory, f)
            return
        else: raise BadArgument

    @commands.command(name="autogrind")
    async def h(self, ctx, action=None):
        if str(ctx.author.id) not in grind: grind[str(ctx.author.id)] = [0, 1, False]
        if action == None:
            if str(ctx.author.id) not in grind or not grind[str(ctx.author.id)][2]: return await ctx.reply("Auto grinding is disabled. Use `.autogrind enable` to enable it")
            return await ctx.reply(f"Level: {grind[str(ctx.author.id)][1]}\nUnclaimed coins: {grind[str(ctx.author.id)][0]}\nEnabled: {grind[str(ctx.author.id)][2]}\nEarnings: {grind[str(ctx.author.id)][1]*(100000 if grind[str(ctx.author.id)][1] < 5 else 500000 if grind[str(ctx.author.id)][1] < 10 else 1000000)} coins/hr")
        elif action == "enable":
            grind[str(ctx.author.id)][2] = True
            await ctx.reply("Enabled auto grinding")
        elif action == "disable":
            grind[str(ctx.author.id)][2] = False
            await ctx.reply("Disabled auto grinding")
        elif action == "upgrade":
            q = 0
            for level in range(grind[str(ctx.author.id)][1]): q += 1000000
            if userdb[str(ctx.author.id)][0] < q: return await ctx.reply("You don't have enough coins to upgrade")
            userdb[str(ctx.author.id)][0] -= q
            grind[str(ctx.author.id)][1] += 1
            await ctx.reply(f"Success! You are now level {grind[str(ctx.author.id)][1]}")
        elif action == "claim":
            if grind[str(ctx.author.id)][0] == 0: return await ctx.reply("You have no coins to claim")
            userdb[str(ctx.author.id)][0] += grind[str(ctx.author.id)][0]
            await ctx.reply(f"You earned {grind[str(ctx.author.id)][0]} coins")
            grind[str(ctx.author.id)][0] = 0
        else: raise BadArgument
        with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
        with open("database/grind.json", "w+") as f: json.dump(grind, f)
    
    @commands.command(name="purse", aliases=["balance", "bal", "coins"])
    async def i(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb: userdb[str(user.id)] = [0, 0, "berserk", [1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 0]
        return await ctx.reply(f"{user} has {userdb[str(user.id)][0]} coins")

    @commands.command(name="equip")
    async def j(self, ctx, item, cl):
        if item not in inventory[str(ctx.author.id)]: return await ctx.reply("You don't own this item")
        classes = ["mage", "archer", "berserk", "tank"]
        if cl not in classes: raise BadArgument
        if item.lower() not in baseitems: raise BadArgument
        if baseitems[item.lower()][len(baseitems[item.lower()])-1] == "armor":
            if userdb[str(ctx.author.id)][classes.index(cl)+8][0] != 0: inventory[str(ctx.author.id)].append(userdb[str(ctx.author.id)][classes.index(cl)+8][0])
            userdb[str(ctx.author.id)][classes.index(cl)+8][0] = item.lower()
        elif baseitems[item.lower()][len(baseitems[item.lower()])-1] == "weapon":
            if userdb[str(ctx.author.id)][classes.index(cl)+8][1] != 0: inventory[str(ctx.author.id)].append(userdb[str(ctx.author.id)][classes.index(cl)+8][1])
            userdb[str(ctx.author.id)][classes.index(cl)+8][1] = item.lower()
        elif baseitems[item.lower()][len(baseitems[item.lower()])-1] == "pet":
            if userdb[str(ctx.author.id)][classes.index(cl)+8][2] != 0: inventory[str(ctx.author.id)].append(userdb[str(ctx.author.id)][classes.index(cl)+8][2])
            userdb[str(ctx.author.id)][classes.index(cl)+8][2] = item.lower()
        inventory[str(ctx.author.id)].remove(item.lower())
        with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
        with open("database/inventory.json", "w+") as f: json.dump(inventory, f)
        return await ctx.reply(f"You equipped your {item} to your {cl} gear")

def setup(client:commands.Bot): client.add_cog(dungeon(client))
