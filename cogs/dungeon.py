import os, sys, json, discord, random, datetime, math, asyncio, time, string
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
#5: defense
#6: price
###pets
#0: strength
#1: crit damage
#2: intelligence
#3: ability damage
#4: health
#5: defense
#6: price
###talismans
#0: strength
#1: intelligence
#2: health
#3: defense
#4: crit damage
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
#13: is in dungeon
#14: slayer levels
    #0: zombie level, xp
    #1: spider level, xp
    #2: enderman level, xp
#15: slayer rng
    #0: zombie
    #1: spider
    #2: enderman
with open("database/inventory.json") as f: inventory = json.load(f)
#key: user id
#0-19: inventory slot
    #0: item
    #1: quantity
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
with open("database/bosses.json") as f: bosses = json.load(f)
with open("database/slayer.json") as f: slayer = json.load(f)
with open("database/shopitems.json") as f: shopitems = json.load(f)
with open("database/sellitems.json") as f: sellitems = json.load(f)
#key: item name
#0: price
#1: type
#2: description/ability
with open("database/talisbag.json") as f: talisbag = json.load(f)
#key: user id
#0: storage (arr)
#1: max storage
classes = ["mage", "archer", "berserk", "tank"]
admins = [706697300872921088, 705462972415213588]

class dungeon(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    def save(self):
        with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
        with open("database/grind.json", "w+") as f: json.dump(grind, f)
        with open("database/inventory.json", "w+") as f: json.dump(inventory, f)
        with open("database/talisbag.json", "w+") as f: json.dump(talisbag, f)

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

    def calculateSurvivalChances(self, floor:int, ehp:int, mode):
        if floor == 1: qw = ehp/500
        elif floor == 2: qw = ehp/1000
        elif floor == 3: qw =  ehp/1500
        elif floor == 4: qw =  ehp/3000
        elif floor == 5: qw =  ehp/3500
        elif floor == 6: qw =  ehp/3500
        elif floor == 7: qw =  ehp/10000
        return qw if mode == "normal" else qw/10 if qw < 10000 else 100

    def calculateDungeonTime(self, floor:int, damage:int, mode="normal"):
        f = int((floor+3)*round(10/(math.log(damage+1, 10)+1), 0) + 1)
        return f if mode == "normal" else 5*f
        
    def applyClassPositives(self, userid:int, damage:int):
        if userdb[str(userid)][2] == "berserk":
            c = 40
            for i in range(userdb[str(userid)][7][0]): c += 1
            return damage*(1 + c/100)
        elif userdb[str(userid)][2] == "archer":
            try:
                if shopitems[userdb[str(userid)][9][2]][1] == "bow":
                    c = 100
                    for i in range(userdb[str(userid)][5][0]): c += 2
                    return damage*(1 + c/100)
                else: return damage
            except KeyError: return damage
        else: return damage

    def calculateTotalStats(self, userid:int, isDungeon:bool=True):
        strength = 1 + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][0] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][1] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][0]
        intelligence = 100 + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][1] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][2] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][3]
        cd = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][4] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][4] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][1]
        cc = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][3] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][1])][3] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][2]
        admg = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][4]
        hp = 100 +  baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][4] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][5]
        defense = baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][0])][5] + baseitems[str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2])][6]
        stats = [strength, intelligence, cd, cc, hp, defense, admg]
        if isDungeon:
            if userdb[str(userid)][2] == "mage":
                for i in range(userdb[str(userid)][4][0]): intelligence += 20
            if userdb[str(userid)][2] == "tank":
                q = 20
                for i in range(userdb[str(userid)][7][0]): q += 1
                defense *= 1 + q/100
        try:
            for item in talisbag[str(userid)][0]:
                strength += baseitems[item][0]
                intelligence += baseitems[item][1]
                hp += baseitems[item][2]
                defense += baseitems[item][3]
                cd += baseitems[item][4]
        except KeyError: pass
        if str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2]) == "sheep": intelligence *= 1.25
        if str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2]) == "blue whale":
            hp *= 1.20
            defense += round(hp/20, 0)
        if str(userdb[str(userid)][classes.index(userdb[str(userid)][2])+8][2]) == "ender dragon":
            arr = []
            for stat in stats: arr.append(round(stat*1.10, 0))
            stats = arr
            del arr
        if isDungeon:
            c = 100
            for i in range(userdb[str(userid)][3][0]): c += 10
            arr = []
            for stat in stats: arr.append(int(round(stat*c/100, 0)))
            return arr
        return stats

    def calculatePercentage(self, current, previous):
        if current == previous: return 100.0
        if current > previous:
            var = (abs(current - previous) / previous) * 100.0
            return 100.0 + var
        try:
            var = (abs(current - previous) / previous) * 100.0
            return 100.0 - var
        except ZeroDivisionError: return 0

    def getSlayerDrop(self, quest, tier, rng):
        if int(tier) < 4: return 0
        adrops = ["0", "scythe blade", "beheaded horror", "shard of the shredded", "warden heart"]
        adroprate = [100-rng if rng <= 100 else 0, 0.16*(int(tier)-3), 0.08*(int(tier)-3), 0.06, 0.01]
        bdrops = ["0", "digested mosquito", "fly swatter"]
        bdroprate = [100-rng if rng <= 100 else 0, 0.06*(int(tier)-3), 0.08*(int(tier)-3)]
        cdrops = ["0", "judgement core", "sinful dice", "pocket espresso machine"]
        cdroprate = [100-rng if rng <= 100 else 0, 0.06*(int(tier)-3), 0.47*(int(tier)-3), 0.39*(int(tier)-3)]
        if rng >= 100:
            adrops.remove("0")
            bdrops.remove("0")
            cdrops.remove("0")
            return random.choice(adrops if quest == "zombie" else bdrops if quest == "spider" else cdrops)
        else: return ''.join(random.choices(adrops if quest == "zombie" else bdrops if quest == "spider" else cdrops, adroprate if quest == "zombie" else bdroprate if quest == "spider" else cdroprate))

    def registerUser(self, userid:int):
        userdb[str(userid)] = [0, 0, "berserk", [1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 0, False, [[0, 0], [0, 0], [0, 0]], [0, 0, 0]]
        self.save()

    async def qq(self):
        while True:
            for user in grind:
                if grind[user][2]: grind[user][0] += grind[user][1]*100000
            self.save()
            await asyncio.sleep(3600)

    @commands.Cog.listener()
    async def on_ready(self): await self.qq()

    @commands.command(name="dungeon", aliases=['d'])
    async def a(self, ctx, floor, mode="normal"):
        if floor == "/dx": return await ctx.reply("no mafs")
        floor = int(floor)
        if floor == 0: return await ctx.reply("ok")
        if floor not in list(range(1,8)): raise BadArgument
        if str(ctx.author.id) not in userdb: self.registerUser(ctx.author.id)
        if mode.lower() == "normal":
            if userdb[str(ctx.author.id)][12] != floor-1 and not userdb[str(ctx.author.id)][12] >= floor: return await ctx.reply("You need to complete the previous floor first")
        elif mode.lower() == "master":
            if userdb[str(ctx.author.id)][12] != floor+6 and not userdb[str(ctx.author.id)][12] >= floor+7: return await ctx.reply("You need to complete the previous floor first")
        else: raise BadArgument
        if userdb[str(ctx.author.id)][13]: return await ctx.reply("You are already in a dungeon")
        stats = self.calculateTotalStats(ctx.author.id)
        if userdb[str(ctx.author.id)][2] == "mage": x = self.calculateAbilityDamage(baseitems[str(userdb[str(ctx.author.id)][8][1])][7], stats[1], stats[6])
        else:
            x = self.calculateDamage(baseitems[str(userdb[str(ctx.author.id)][11][1])][0], stats[0], stats[2])
            x = self.applyClassPositives(ctx.author.id, x)
        y = self.calculateDungeonTime(floor, x, mode.lower())
        z = self.calculateSurvivalChances(floor, self.calculateEffectiveHealth(stats[4], stats[5]), mode)
        if mode == "normal": r = int(''.join(random.choices([str(100000*floor), str(1000000*floor), str(100000000*floor)], [100, 0.15*floor, 0.04*floor], k=1)))
        else: r = int(''.join(random.choices([str(100000*(floor+7)), str(1000000*(floor+7)), str(100000000*(floor+7))], [100, 0.15*(floor+7), 0.04*(floor+7)], k=1)))
        cxp = [random.randint(100, 500), random.randint(500, 1000), random.randint(1000, 3000), random.randint(3000, 7000), random.randint(7000, 20000), random.randint(20000, 50000), random.randint(50000, 100000)]
        if mode == "master":
            for i in cxp: cxp[cxp.index(i)] *= 10
        clxp = round(cxp[floor-1]/1.5, 0)
        await ctx.reply(f"You entered the Catacombs {'Floor' if mode.lower() == 'normal' else 'Master Mode'} {floor}, come back in {y} minutes to check your rewards")
        userdb[str(ctx.author.id)][13] = True
        with open("database/userdb.json", "w+") as f: json.dump(userdb, f)
        if z >= 100: s = [True]
        else: s = random.choices([False, True], [100-z, z], k=1)
        if not s[0]:
            if ctx.author.id != 705462972415213588: await asyncio.sleep(20)
            await ctx.author.send(f"You died in the dungeon. You earned:\n+{round(cxp[floor-1]/10, 0)} catacombs experience\n+{round(clxp/10, 0)} {userdb[str(ctx.author.id)][2]} experience")
            a1 = round(cxp[floor-1]/10, 0)
            a2 = round(clxp/10, 0)
            comp = False
        else:
            if ctx.author.id != 705462972415213588: await asyncio.sleep(float(y*60))
            await ctx.author.send(f"You completed the dungeons floor {floor}. You earned:\n+{cxp[floor-1]} catacombs experience\n+{clxp} {userdb[str(ctx.author.id)][2]} experience\n+{r} coins")
            a1 = round(cxp[floor-1], 0)
            a2 = round(clxp, 0)
            comp = True
        userdb[str(ctx.author.id)][0] += r
        xp = 0
        for i in range(userdb[str(ctx.author.id)][3][0]): xp += (i+1)*50000
        userdb[str(ctx.author.id)][3][1] += a1
        if userdb[str(ctx.author.id)][3][1] >= xp:
            userdb[str(ctx.author.id)][3][0] += 1
            userdb[str(ctx.author.id)][3][1] = 0
        userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][1] += a2
        clxp = 0
        for i in range(userdb[str(ctx.author.id)][3][0]): clxp += (i+1)*25000
        if userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][1] >= clxp:
            userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][0] += 1
            userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+4][1] = 0
        if comp:
            if userdb[str(ctx.author.id)][12] == floor-1 if mode == "normal" else floor+6: userdb[str(ctx.author.id)][12] += 1
        userdb[str(ctx.author.id)][13] = False
        self.save()

    @commands.command(name="selectclass", aliases=["setclass", "class"])
    async def b(self, ctx, x:str):
        if x.lower() not in classes: raise BadArgument
        userdb[str(ctx.author.id)][2] = x.lower()
        self.save()
        return await ctx.reply(f"you changed your class to {x.lower()}")

    @commands.command(name="stats")
    async def c(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb:
            if str(user.id) not in userdb: self.registerUser(user.id)
        stats1 = self.calculateTotalStats(user.id, False)
        stats2 = self.calculateTotalStats(user.id, True)
        if userdb[str(user.id)][2] == "mage":
            x2 = self.calculateAbilityDamage(baseitems[str(userdb[str(user.id)][8][1])][7], stats2[1], stats2[6])
            x1 = self.calculateAbilityDamage(baseitems[str(userdb[str(user.id)][8][1])][7], stats1[1], stats1[6])
        else:
            x2 = self.calculateDamage(baseitems[userdb[str(user.id)][classes.index(userdb[str(user.id)][2])+8][1]][0], stats2[0], stats2[2])
            x1 = self.calculateDamage(baseitems[userdb[str(user.id)][classes.index(userdb[str(user.id)][2])+8][1]][0], stats1[0], stats1[2])
        e = discord.Embed(title=f"{user}'s stats", description=f"Health: {stats1[4]} ({stats2[4]})\nDefense: {stats1[5]} ({stats2[5]})\nEffective health: {int(self.calculateEffectiveHealth(stats1[4], stats1[5]))} ({int(self.calculateEffectiveHealth(stats2[4], stats2[5]))})\nStrength: {stats1[0]} ({stats2[0]})\nCritical Damage: {stats1[2]} ({stats2[2]})\nIntelligence: {stats1[1]} ({stats2[1]})\nAbility Damage: {stats1[6]} ({stats2[6]})\nEstimated damage: {int(x1)} ({int(x2)})", color=discord.Color.random())
        return await ctx.reply(embed=e)
    
    @commands.command(name="info")
    async def d(self, ctx, floor, mode="normal"):
        if int(floor) not in list(range(1, 8)): raise BadArgument
        if mode.lower() != "normal" and mode.lower() != "master": raise BadArgument
        e = discord.Embed(title=f"floor {floor} info", description=f"Boss: {bosses[floor][0]}\nBoss health: {bosses[floor][1][0 if mode.lower() == 'normal' else 1]}\nDungeon size: {bosses[floor][2]}\n\n{bosses[floor][3]}", color=discord.Color.random())
        return await ctx.reply(embed=e)

    @commands.command(name="level")
    async def e(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb: self.registerUser(user.id)
        xp = mxp = axp = txp = bxp = 0
        for i in range(userdb[str(user.id)][3][0]): xp += (i+1)*50000
        for i in range(userdb[str(user.id)][4][0]): mxp += (i+1)*25000
        for i in range(userdb[str(user.id)][5][0]): axp += (i+1)*25000
        for i in range(userdb[str(user.id)][6][0]): bxp += (i+1)*25000
        for i in range(userdb[str(user.id)][7][0]): txp += (i+1)*25000
        xp1 = round(self.calculatePercentage(userdb[str(user.id)][3][1], xp), 1)
        mxp1 = round(self.calculatePercentage(userdb[str(user.id)][4][1], mxp), 1)
        axp1 = round(self.calculatePercentage(userdb[str(user.id)][5][1], axp), 1)
        bxp1 = round(self.calculatePercentage(userdb[str(user.id)][6][1], bxp), 1)
        txp1 = round(self.calculatePercentage(userdb[str(user.id)][7][1], txp), 1)
        embed = discord.Embed(title=f"{user}'s level info", description=f"Catacombs level: {userdb[str(user.id)][3][0]} ({userdb[str(user.id)][3][1]}/{xp} {xp1}%)\nMage level: {userdb[str(user.id)][4][0]} ({userdb[str(user.id)][4][1]}/{mxp} {mxp1}%)\nArcher level: {userdb[str(user.id)][5][0]} ({userdb[str(user.id)][5][1]}/{axp} {axp1}%)\nBerserk level: {userdb[str(user.id)][6][0]} ({userdb[str(user.id)][6][1]}/{bxp} {bxp1}%)\nTank level: {userdb[str(user.id)][7][0]} ({userdb[str(user.id)][7][1]}/{txp} {txp1}%)\nClass average: {round((userdb[str(user.id)][4][0]+userdb[str(user.id)][5][0]+userdb[str(user.id)][6][0]+userdb[str(user.id)][7][0])/4, 1)}", color=discord.Color.random())
        return await ctx.reply(embed=embed)
    
    @commands.command(name="inventory", aliases=["inv"])
    async def f(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in inventory or len(inventory[str(user.id)]) == 0: e = discord.Embed(title=f"{user}'s inventory", description="This user has no items", color=discord.Color.random())
        else:
            x = str()
            for i in range(len(inventory[str(user.id)])): x += f"slot {i+1}: {inventory[str(user.id)][i][0]} {str(inventory[str(user.id)][i][1]) + 'x' if inventory[str(user.id)][i][1] > 1 else ''}\n"
            e = discord.Embed(title=f"{user}'s inventory", description=x, color=discord.Color.random())
        return await ctx.reply(embed=e)
    
    @commands.command(name="auction", aliases=["a"])
    async def g(self, ctx, action:str, item:str=None, price:int=None, t:int=None):
        if action == "create":
            if len(list(auctions.keys())) >= 10: return await ctx.reply("the auctions queue is full")
            o = len(list(auctions.keys()))
            if item == None: raise MissingRequiredArgument
            if price == None: raise MissingRequiredArgument
            if t == None: raise MissingRequiredArgument
            inInventory = False
            for i in inventory[str(ctx.author.id)]:
                if i[0] == item.lower() and item not in baseitems:
                    q = inventory[str(ctx.author.id)].index(i)
                    inInventory = True
                    break
            if not inInventory: return await ctx.reply(f"You dont own this item")
            if t > 1440: return await ctx.reply(f"Time should not be more than 24 hours")
            if t < 5: return await ctx.reply(f"Time should not be less than 5 minutes")
            if price <= 0: raise BadArgument
            if inventory[str(ctx.author.id)][q][1] == 1: inventory[str(ctx.author.id)].remove(inventory[str(ctx.author.id)][q])
            else: inventory[str(ctx.author.id)][q][1] -= 1
            auctions[str(o)] = [item.lower(), price, time.time()+(t*60), ctx.author.id]
            with open("database/auctions.json", "w+") as f: json.dump(auctions, f)
            self.save()
            e = discord.Embed(title="You created an auction", description=f"Item: {item.lower()}\nPrice: {price}\nEnds: <t:{int(time.time()+(t*60))}:R>", color=discord.Color.green())
            return await ctx.reply(embed=e)
        elif action == "cancel":
            if item == None: raise MissingRequiredArgument
            if item not in list(auctions.keys()): return await ctx.reply("Invalid auction id")
            if auctions[item][3] != ctx.author.id: return await ctx.reply("This isn't your auction")
            if len(inventory[str(ctx.author.id)]) == 20: return await ctx.reply("Your inventory is full")
            o = False
            for i in inventory[str(ctx.author.id)]:
                if i[0] == auctions[item][0] and auctions[item][0] in sellitems:
                    q = inventory[str(ctx.author.id)].index(i)
                    o = True
                    break
            if o: inventory[str(ctx.author.id)][q][1] += 1
            else: inventory[str(ctx.author.id)].append([auctions[item][0], 1])
            del auctions[item]
            with open("database/auctions.json", "w+") as f: json.dump(auctions, f)
            self.save()
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
            if len(inventory[str(ctx.author.id)]) == 20: return await ctx.reply("Your inventory is full")
            userdb[str(ctx.author.id)][0] -= auctions[item][1]
            userdb[str(auctions[item][3])][0] += auctions[item][1]
            if str(ctx.author.id) not in inventory: inventory[str(ctx.author.id)] = list()
            #inventory[str(ctx.author.id)].append(auctions[item][0])
            q = None
            for i in inventory[str(ctx.author.id)]:
                if i[0] == auctions[item][0] and auctions[item][0] in list(sellitems.keys()):
                    isStackable = True
                    q = i
                    break
                isStackable = False
            if isStackable: inventory[str(ctx.author.id)][inventory(str.ctx.author.id).index(q)][1] += 1
            else: inventory[str(ctx.author.id)].append([auctions[item][0], 1])
            await ctx.reply(f"You bought a {auctions[item][0]} for {auctions[item][1]} coins")
            u = await self.client.fetch_user(auctions[item][3])
            await u.send(f"{ctx.author} bought your {auctions[item][0]} for {auctions[item][1]} coins")
            del auctions[item]
            with open("database/auctions.json", "w+") as f: json.dump(auctions, f)
            self.save()
            return
        else: raise BadArgument

    @commands.command(name="autogrind")
    async def h(self, ctx, action=None):
        if str(ctx.author.id) not in grind: grind[str(ctx.author.id)] = [0, 1, False]
        if action == None:
            if str(ctx.author.id) not in grind or not grind[str(ctx.author.id)][2]: return await ctx.reply("Auto grinding is disabled. Use `.autogrind enable` to enable it")
            return await ctx.reply(f"Level: {grind[str(ctx.author.id)][1]}\nUnclaimed coins: {grind[str(ctx.author.id)][0]}\nEnabled: {grind[str(ctx.author.id)][2]}\nEarnings: {grind[str(ctx.author.id)][1]*(100000 if grind[str(ctx.author.id)][1] < 5 else 500000 if grind[str(ctx.author.id)][1] < 10 else 1000000)}coins/hr")
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
        self.save()
    
    @commands.command(name="purse", aliases=["balance", "bal", "coins"])
    async def i(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb: self.registerUser(user.id)
        return await ctx.reply(f"{user} has {userdb[str(user.id)][0]} coins")

    @commands.command(name="equip")
    async def j(self, ctx, item, cl):
        if item not in inventory[str(ctx.author.id)]: return await ctx.reply("You don't own this item")
        if cl not in classes: raise BadArgument
        if item.lower() not in baseitems: raise BadArgument
        if baseitems[item.lower()][len(baseitems[item.lower()])-1] == "armor":
            if userdb[str(ctx.author.id)][classes.index(cl)+8][0] != 0: inventory[str(ctx.author.id)].append([userdb[str(ctx.author.id)][classes.index(cl)+8][0], 1])
            userdb[str(ctx.author.id)][classes.index(cl)+8][0] = item.lower()
        elif baseitems[item.lower()][len(baseitems[item.lower()])-1] == "weapon":
            if userdb[str(ctx.author.id)][classes.index(cl)+8][1] != 0: inventory[str(ctx.author.id)].append([userdb[str(ctx.author.id)][classes.index(cl)+8][1], 1])
            userdb[str(ctx.author.id)][classes.index(cl)+8][1] = item.lower()
        elif baseitems[item.lower()][len(baseitems[item.lower()])-1] == "pet":
            if userdb[str(ctx.author.id)][classes.index(cl)+8][2] != 0: inventory[str(ctx.author.id)].append([userdb[str(ctx.author.id)][classes.index(cl)+8][2], 1])
            userdb[str(ctx.author.id)][classes.index(cl)+8][2] = item.lower()
        inventory[str(ctx.author.id)].remove([item.lower(), 1])
        self.save()
        return await ctx.reply(f"You equipped your {item} to your {cl} gear")
    
    @commands.command(name="unequip")
    async def k(self, ctx, item, cl):
        q = ["armor", "weapon", "pet"]
        if item not in baseitems: return await ctx.reply("this item does not exist")
        if item != userdb[str(ctx.author.id)][classes.index(cl.lower())+8][q.index(baseitems[item][len(baseitems[item])-1])]: return await ctx.reply("you dont own this item")
        if len(inventory[str(ctx.author.id)]) == 20: return await ctx.reply("your inventory is full")
        inventory[str(ctx.author.id)].append([userdb[str(ctx.author.id)][classes.index(cl.lower())+8][q.index(baseitems[item][len(baseitems[item])-1])], 1])
        userdb[str(ctx.author.id)][classes.index(cl.lower())+8][q.index(baseitems[item][len(baseitems[item])-1])] = 0
        self.save()
        return await ctx.reply(f"You unequipped your {item} from your {cl} gear")

    @commands.command(name="gear", aliases=["getgear"])
    async def l(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb: self.registerUser(user.id)
        q = str()
        for i in range(4):
            q += f"{classes[i]}: "
            for x in range(3):
                if userdb[str(user.id)][i+8][x] != 0: q += f"{userdb[str(user.id)][i+8][x]}{',' if x != 2 else ''} "
            q += "\n"
        return await ctx.reply(embed=discord.Embed(title=f"{user}'s gear", description=q, color=discord.Color.random()))
    
    @commands.command(name="createitem")
    async def m(self, ctx, name, _type, _str:int=0, cd:int=0, _int:int=0, admg:int=0, dmg:int=0, baseadmg:int=0, hp:int=0, _def:int=0):
        if not ctx.author.id == 705462972415213588: return
        if name in baseitems: return await ctx.reply("an item with this name already exists")
        if _type == "weapon": baseitems[name] = [dmg, _str, _int, 0, cd, 0, 0, baseadmg, _type]
        elif _type == "armor": baseitems[name] = [_str, _int, 0, cd, hp, _def, 0, _type]
        elif _type == "pet": baseitems[name] = [_str, cd, _int, admg, hp, _def, 0, _type]
        with open("database/baseitems.json", "w+") as f: json.dump(baseitems, f)
        return await ctx.reply(f"created an item with name {name}")

    @commands.command(name="additem")
    async def n(self, ctx, item, user:discord.User):
        if not ctx.author.id == 705462972415213588: return
        if str(user.id) not in inventory: inventory[str(user.id)] = list()
        if len(inventory[str(user.id)]) == 20: return await ctx.reply("the inventory of that user is full")
        if item not in baseitems and item not in sellitems: return await ctx.reply("that item doesnt exist")
        q = None
        for i in inventory[str(user.id)]:
            if i[0] == item.lower():
                q = i
                break
        if q == None or q not in inventory[str(user.id)]: inventory[str(user.id)].append([item.lower(), 1])
        else: inventory[str(user.id)][inventory[str(user.id)].index(q)][1] += 1
        self.save()
        return await ctx.reply(f"Added a {item} to {user}'s inventory")
    
    @commands.command(name="addcoins")
    async def o(self, ctx, amount:int, user=discord.User):
        if not ctx.author.id == 705462972415213588: return
        if str(user.id) not in userdb: self.registerUser(user.id)
        userdb[str(user.id)][0] += amount
        self.save()
        return await ctx.reply(f"added {amount} coins to {user}'s profile")

    @commands.command(name="help")
    async def p(self, ctx, command=None):
        if command == None: e = discord.Embed(title="help", description="auction, autogrind, gear, dungeon, stats, equip, unequip, setclass, inventory, level, info", color=discord.Color.random())
        elif command == "help":
            e = discord.Embed(title="help for command help", description="helps", color=discord.Color.random())
            e.set_footer(text="why tf do you even need help with this command")
        elif command == "auction": e = discord.Embed(title="help for command auction", description="creates an auction for an item\nusage:\n.auction create item price time(minutes)\n.auction cancel id\n.auction list\n.auction buy id", color=discord.Color.random())
        elif command == "autogrind": e = discord.Embed(title="help for command autogrind", description="gets coins while you are offline\nusage:\n.autogrind enable/disable\n.autogrind claim\n.autogrind upgrade\n.autogrind", color=discord.Color.random())
        elif command == "gear": e = discord.Embed(title="help for command gear", description="shows the gear of a user for each class\nusage:\n.gear user(optional)", color=discord.Color.random())
        elif command == "dungeon": e = discord.Embed(title="help for command dungeon", description="enters a dungeon\nusage:\n.dungeon 1-7", color=discord.Color.random())
        elif command == "stats": e = discord.Embed(title="help for command stats", description="shows the stats of a user\nusage:\n.stats user(optional)", color=discord.Color.random())
        elif command == "equip": e = discord.Embed(title="help for command equip", description="equips an item into the specified class\nusage:\n.equip item class", color=discord.Color.random())
        elif command == "unequip": e = discord.Embed(title="help for command unequip", description="uneqips an item from the specified class\nusage: .unequip item class", color=discord.Color.random())
        elif command == "setclass": e = discord.Embed(title="help for command setclass", description="changes your class\nusage:\n.setclass class", color=discord.Color.random())
        elif command == "inventory": e = discord.Embed(title="help for command inventory", description="shows the inventory of a user\nusage:\n.inventory user(optional)", color=discord.Color.random())
        elif command == "info": e = discord.Embed(title="help for command info", description="shows information about a dungeon floor\nusage:\n.info 1-7", color=discord.Color.random())
        elif command == "level": e = discord.Embed(title="help for command level", description="shows the class levels of a user\nusage:\n.level user(optional)", color=discord.Color.random())
        return await ctx.reply(embed=e)

    @commands.command(name="shop")
    async def q(self, ctx, *, item=None):
        if item == None:
            qw = dict(sorted(shopitems.items(), key=lambda x:x[1][0]))
            col = discord.Color.random()
            try:
                if "seal of the family" in talisbag[str(ctx.author.id)][0]: hasDiscount = True
                else: hasDiscount = False
            except KeyError: hasDiscount = False
            a = list(qw.keys())
            l = int(len(list(qw.keys()))/3)
            prices = list()
            for q in list(qw.values()):
                prices.append(q[0])
            q1 = q2 = q3 = str()
            l1 = l2 = l3 = list()
            q = 0
            o = 0
            for i in range(int(len(list(qw.keys()))/2)): q1 +=f"{string.capwords(list(qw.keys())[i])}\n"+"    Price: {:,} coins\n\n".format(int(qw[list(qw.keys())[i]][0]*0.97) if hasDiscount else qw[list(qw.keys())[i]][0])
            for i in range(int(len(list(qw.keys()))/2), int(len(list(qw.keys())))): q2 += f"{string.capwords(list(qw.keys())[i])}\n"+"    Price: {:,} coins\n\n".format(int(qw[list(qw.keys())[i]][0]*0.97) if hasDiscount else qw[list(qw.keys())[i]][0])
            # for i in range(3):
            #     for b in range(l):
            #         try:
            #             #locals()[f"q{str(i+1)}"] += f"{string.capwords(a[b])}\n"+"    Price: {:,} coins\n\n".format(int(qw[a[b]][0]*0.97) if hasDiscount else qw[a[b]][0])
            #             locals()[f"q{str(i+1)}"] += f"{string.capwords(a[b])}\n"+"    Price: {:,} coins\n\n".format(int(prices[b]*0.97) if hasDiscount else prices[b])
            #             del qw[a[b]]
            #         except IndexError: break
            p1 = discord.Embed(title="shop", description=q1, color=col)
            p2 = discord.Embed(title="shop", description=q2, color=col)
            p3 = discord.Embed(title="shop", description=q3, color=col)
            p1.set_footer(text="Page 1/3")
            p2.set_footer(text="Page 2/3")
            #p3.set_footer(text="Page 3/3")
            p = [p1, p2]
            message = await ctx.send(embed=p1)
            await message.add_reaction('◀')
            await message.add_reaction('▶')
            def check(reaction, user): return user == ctx.author
            i = 0
            reaction = None
            while True:
                if str(reaction) == '◀':
                    if i > 0:
                        i -= 1
                        await message.edit(embed=p[i])
                elif str(reaction) == '▶':
                    if i < 1:
                        i += 1
                        await message.edit(embed=p[i])
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout = 30.0, check = check)
                    await message.remove_reaction(reaction, user)
                except: break
            await message.clear_reactions()
        else:
            if item.lower() not in list(shopitems.keys()): raise BadArgument
            q = str()
            if shopitems[item.lower()][1] == "bow" or shopitems[item.lower()][1] == "sword": s = ["Damage", "Strength", "Intelligence", "Crit chance", "Crit damage"]
            elif shopitems[item.lower()][1] == "armor": s = ["Strength", "Intelligence", "Crit chance", "Crit damage", "Health", "Defense"]
            elif shopitems[item.lower()][1] == "pet": s = ["Strength", "Crit damage", "Intelligence", "Ability damage", "Health", "Defense"]
            elif shopitems[item.lower()][1] == "talisman": s = ["Strength", "Intelligence", "Health", "Defense", "Crit damage"]
            for i in range(len(s)):
                if baseitems[item][i] != 0: q += f"{s[i]} - {baseitems[item][i]}\n"
            e = discord.Embed(title=f"{string.capwords(item)}", description=f"Type: {shopitems[item.lower()][1]}\n{'Stats:' if len(q) > 0 else ''}\n{q}\n{shopitems[item.lower()][2] if shopitems[item.lower()][2] is not None else ''}", color=discord.Color.random())
            return await ctx.reply(embed=e)

    @commands.command(name="buy")
    async def r(self, ctx, *, item):
        if item.lower() not in list(shopitems.keys()): return await ctx.reply("This item does not exist, type `.shop` to get the item list")
        if shopitems[item.lower()][0] > userdb[str(ctx.author.id)][0]: return await ctx.reply("You don't have enough money to buy this item")
        if len(inventory[str(ctx.author.id)]) >= 20 and shopitems[item.lower()][1] != "talisman": return await ctx.reply("You don't have enough space in your inventory")
        try:
            if "seal of the family" in talisbag[str(ctx.author.id)][0]: hasDiscount = True
            else: hasDiscount = False
        except KeyError: hasDiscount = False
        if shopitems[item.lower()][1] == "talisman":
            if str(ctx.author.id) not in talisbag: talisbag[str(ctx.author.id)] = [[], 5]
            if len(talisbag[str(ctx.author.id)][0]) >= talisbag[str(ctx.author.id)][1]: return await ctx.reply("You don't have enough space in your talisman bag")
            if item.lower() in talisbag[str(ctx.author.id)][0]: return await ctx.reply("You aready own this talisman")
            talisbag[str(ctx.author.id)][0].append(item.lower())
        else:
            if len(inventory[str(ctx.author.id)]) >= 20: return await ctx.reply("Your inventory is full")
            inventory[str(ctx.author.id)].append([item.lower(), 1])
        await ctx.reply(f"You bought a {string.capwords(item)} for {int(shopitems[item.lower()][0]*0.97) if hasDiscount else shopitems[item.lower()][0]} coins")
        userdb[str(ctx.author.id)][0] -= int(shopitems[item.lower()][0]*0.97) if hasDiscount else shopitems[item.lower()][0]
        self.save()
    
    @commands.command(name="talismans", aliases=["talisman", "talis"])
    async def s(self, ctx, *, action=None):
        if action == None:
            if str(ctx.author.id) not in talisbag or len(talisbag[str(ctx.author.id)][0]) == 0: return await ctx.reply("You don't own any talismans")
            q = str()
            for i in talisbag[str(ctx.author.id)][0]: q += f"slot {talisbag[str(ctx.author.id)][0].index(i)+1}. {i}"
            e = discord.Embed(title=f"{ctx.author.display_name}'s talisman bag", description=q, color=discord.Color.random())
            e.set_footer(text=f"Upgrade cost: {str((talisbag[str(ctx.author.id)][1]/5)*500000)}")
            return await ctx.reply(embed=e)
        elif action.lower() == "upgrade":
            if talisbag[str(ctx.author.id)][1] == 20: return await ctx.reply("Your talisman bag is already maxed out")
            q = (talisbag[str(ctx.author.id)][1]/5)*500000
            if q > userdb[str(ctx.author.id)][0]: return await ctx.reply("You don't have enough money to upgrade")
            talisbag[str(ctx.author.id)][1] += 5
            userdb[str(ctx.author.id)][0] -= q
            self.save()
            return await ctx.reply("You upgraded your talisman bag successfully")

    @commands.command(name="slayer")
    async def t(self, ctx, quest, tier):
        stats = self.calculateTotalStats(ctx.author.id, False)
        dmg = self.calculateDamage(baseitems[userdb[str(ctx.author.id)][classes.index(userdb[str(ctx.author.id)][2])+8][1]][0], stats[0], stats[2])
        ehp = self.calculateEffectiveHealth(stats[4], stats[5])
        l = [5, 25, 200, 1000, 5000, 20000, 100000, 400000, 1000000]
        if quest.lower() not in slayer.keys(): raise BadArgument
        if tier not in slayer[quest.lower()].keys(): raise BadArgument
        if slayer[quest.lower()][tier][0] > userdb[str(ctx.author.id)][0]: return await ctx.reply("You don't have enough money to start this quest")
        if slayer[quest.lower()][tier][1]/dmg > ehp/slayer[quest.lower()][tier][2]: s = False
        else: s = True
        userdb[str(ctx.author.id)][0] -= slayer[quest.lower()][tier][0]
        await ctx.reply(f"You started a tier {tier} {quest.lower()} quest")
        if not s: await ctx.author.send("You died in your slayer quest")
        else:
            drop = self.getSlayerDrop(quest.lower(), tier, userdb[str(ctx.author.id)][15][list(slayer.keys()).index(quest.lower())])
            msg = f"You completed your slayer quest successfully!\nYou earned {slayer[quest.lower()][tier][3]} slayer xp"
            if int(tier) >= 4:
                if drop != "0":
                    inInventory = False
                    q = None
                    for i in inventory[str(ctx.author.id)]:
                        if i[0] == drop:
                            inInventory = True
                            q = i
                            break
                    msg += f"\n**CRAZY RARE DROP** {string.capwords(drop)}"
                    userdb[str(ctx.author.id)][15][list(slayer.keys()).index(quest.lower())] = 0
                    if inInventory: inventory[str(ctx.author.id)][inventory[str(ctx.author.id)].index(q)][1] += 1
                    else: inventory[str(ctx.author.id)].append([drop, 1])
                rng = round(random.random(), 1)
                userdb[str(ctx.author.id)][15][list(slayer.keys()).index(quest.lower())] += rng
                msg += f"\n+{rng}% rng ({round(userdb[str(ctx.author.id)][15][list(slayer.keys()).index(quest.lower())], 1)}% total)"
            userdb[str(ctx.author.id)][14][list(slayer.keys()).index(quest.lower())][1] += slayer[quest.lower()][tier][3]
            if userdb[str(ctx.author.id)][14][list(slayer.keys()).index(quest.lower())][0] < 9:
                if userdb[str(ctx.author.id)][14][list(slayer.keys()).index(quest.lower())][1] >= l[userdb[str(ctx.author.id)][14][list(slayer.keys()).index(quest.lower())][0]-1]:
                    userdb[str(ctx.author.id)][14][list(slayer.keys()).index(quest.lower())][0] += 1
            await ctx.send(msg)
        self.save()

    @commands.command()
    async def setrng(self, ctx, user:discord.User, rate:float, quest):
        if ctx.message.author.id not in admins: return
        userdb[str(ctx.author.id)][15][list(slayer.keys()).index(quest.lower())] = rate
        self.save()
        return await ctx.reply(f"Set rng rate of {user.display_name} to {rate}%")
    
    @commands.command(name="slayerinfo")
    async def u(self, ctx, quest, tier:str):
        if quest.lower() not in list(slayer.keys()): raise BadArgument
        if tier not in slayer[quest.lower()].keys(): raise BadArgument
        e = discord.Embed(title=f"{quest.lower()} tier {tier} info", description=f"Health: {slayer[quest.lower()][tier][1]}\nDamage per second: {slayer[quest.lower()][tier][2]}\nStarting cost: {slayer[quest.lower()][tier][0]}\nxp: {slayer[quest.lower()][tier][3]}", color=discord.Color.random())
        await ctx.reply(embed=e)

    @commands.command(name="slayerlevel")
    async def v(self, ctx, user:discord.User=None):
        if user == None: user = ctx.author
        if str(user.id) not in userdb: self.registerUser(user.id)
        e = discord.Embed(title=f"{user.display_name}'s slayer levels", description=f"Zombie slayer level: {userdb[str(ctx.author.id)][14][0][0]}\nSpider slayer level:  {userdb[str(ctx.author.id)][14][1][0]}\nEnderman slayer level:  {userdb[str(ctx.author.id)][14][2][0]}", color=discord.Color.random())
        return await ctx.reply(embed=e)
    
    @commands.command(name="sell")
    async def w(self, ctx, item, quantity:int=1):
        if item.lower() not in sellitems and item.lower() not in shopitems: return await ctx.reply("This item does not exist")
        if quantity <= 0: raise BadArgument
        inInventory = False
        q = 0
        for i in inventory[str(ctx.author.id)]:
            if i[0] == item.lower():
                inInventory = True
                q = inventory[str(ctx.author.id)].index(i)
                break
        if inInventory == False: return await ctx.reply("You don't own this item")
        if inventory[str(ctx.author.id)][q][1] < quantity: return await ctx.reply(f"You dont own that many {string.capwords(item)}s")
        if inventory[str(ctx.author.id)][q][1] == 1: del inventory[str(ctx.author.id)][q]
        else: inventory[str(ctx.author.id)][q][1] -= quantity
        if item.lower() in sellitems: userdb[str(ctx.author.id)][0] += sellitems[item.lower()]*quantity
        if item.lower() in shopitems: (userdb[str(ctx.author.id)][0]/2)*quantity
        self.save()
        return await ctx.reply(f"You sold {str(quantity)} {string.capwords(item)}{'s' if quantity > 1 else ''}")

def setup(client:commands.Bot):
    client.add_cog(dungeon(client))
