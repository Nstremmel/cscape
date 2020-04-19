import discord
import asyncio
import random
import time
import datetime
import os
import psycopg2
from discord.utils import get

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()
conn.set_session(autocommit=True)

c.execute("DROP TABLE rsmoney")
c.execute("""CREATE TABLE rsmoney (
              id bigint,
              osrs bigint,
              ikov bigint,
              spawnpk bigint,
              runewild bigint,
              zenyte bigint,
              roatzpk bigint,
              privacy boolean,
              openchannel bigint
              )""")
conn.commit()

# c.execute("DROP TABLE duels")
# c.execute("""CREATE TABLE duels (
#               id bigint,
#               currency text,
#               bet integer,
#               type text,
#               messageid bigint,
#               channelid bigint,
#               )""")
# conn.commit()

client = discord.Client()

def add_member(userid):
    c.execute('INSERT INTO rsmoney VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (userid, 0, 0, 0, 0, 0, 0, False, 0))

def getvalue(userid, column):
    strings=[]
    booleans=[]

    if column == '07':
        column = 'osrs'
    try:
        c.execute("SELECT osrs FROM rsmoney WHERE id={}".format(userid))
        tester=int(c.fetchone()[0])
    except:
        print("New Member")
        add_member(int(userid))
        return 0

    c.execute("SELECT {} FROM rsmoney WHERE id={}".format(column, userid))

    if column in booleans:
        return bool(c.fetchone()[0])
    elif column in strings:
        return str(c.fetchone()[0])
    else:
        return int(c.fetchone()[0])

def update_money(userid, currency, amount):
    if currency == '07':
        currency = 'osrs'
    total = getvalue(int(userid), currency)
    c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, total + amount, userid))

def isstaff(authorroles):
    for i in open('staff.txt'):
        guild = client.get_guild(550630947767320578)
        role = get(guild.roles, name=str(i.strip()))
        if role in authorroles:
            return 'verified'

def formatok(amount):
    if amount[-1:].lower() == 'm':
        return int(float(str(amount[:-1])) * 1000)
    elif amount[-1:].lower() == 'k':
        return int(float(str(amount[:-1])))
    elif amount[-1:].lower() == 'b':
        return int(float(str(amount[:-1])) * 1_000_000)
    else:
        return int(float(amount)*1000)

def formatfromk(amount):
    if amount>=1000000:
        if len(str(amount))==7:
            return '{0:.3g}'.format(amount*0.000001)+"B"
        elif len(str(amount))==8:
            return '{0:.4g}'.format(amount*0.000001)+"B"
        else:
            return '{0:.5g}'.format(amount*0.000001)+"B"
    elif amount>=1000:
        if len(str(amount))==4:
            return '{0:.3g}'.format(amount*0.001)+"M"
        elif len(str(amount))==5:
            return '{0:.4g}'.format(amount*0.001)+"M"
        elif len(str(amount))==6:
            return '{0:.5g}'.format(amount*0.001)+"M"
    else:
        return str(amount)+"k"


def hpupdate(players, url, dueltype):
    embed = discord.Embed(color=16766463)
    embed.set_author(name='Fight to the Death!', icon_url=url)
    for i in players:
        hp = int(i[1])
        if hp in range(76, 100):
            hp = get(client.emojis, name='hpbar100')
        elif hp in range(51, 76):
            hp = get(client.emojis, name='hpbar75')
        elif hp in range(26, 51):
            hp = get(client.emojis, name='hpbar50')
        elif hp in range(1, 26):
            hp = get(client.emojis, name='hpbar25')
        elif hp < 1:
            hp = get(client.emojis, name='hpbar0')
        rocktail = get(client.emojis, name='rocktail')
        if dueltype=="mele":
            embed.add_field(name=str(i[0])[:-5], value="Poisoned: "+str(i[4]) +
                                                        "\n"+str(rocktail)+": "+str(i[2]) +
                                                        "\nSpecial Attack: "+str(i[3]*25)+"%" +
                                                        "\nHP Left: "+str(i[1])+" "+str(hp), inline=True)
        elif dueltype=="magic":
            embed.add_field(name=str(i[0])[:-5], value= "\n"+str(rocktail)+": "+str(i[2]) +
                                                        "\nFrozen: "+str(i[3]) +
                                                        "\nHP Left: "+str(i[1])+" "+str(hp), inline=True)
    return embed

def isenough(amount, currency):
    if amount < 100:
        words = 'The minimum amount you can bet is **10k** gp ' + currency + '.'
        return (False, words)
    else:
        return (True, ' ')
##############################################################################################################

#Predefined Variables
colors = ['A', 'B', 'C', 'D', 'E', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
flowers = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']
sidecolors = [16711680, 16743712, 16776960, 1305146, 1275391, 16730111]
meleduel = False
magicduel = False

class currencies():
    osrs, ikov, spawnpk, runewild, zenyte, roatzpk = [0, 'osrs'], [0, 'ikov'], [0, 'spawnpk'], [0, 'runewild'], [0, 'zenyte'], [0, 'roatzpk']
    currencies = [osrs, ikov, spawnpk, runewild, zenyte, roatzpk]

async def my_background_task():
    await client.wait_until_ready()
    while (not client.is_closed):
        None
        await asyncio.sleep(600)

@client.event
async def on_ready():
    print('Bot Logged In!')

@client.event
async def on_raw_reaction_add(payload):
    user = client.get_user(payload.user_id)
    channel = client.get_channel(payload.channel_id)
    category1 = get(channel.guild.categories, name = 'rs services')
    category2 = get(channel.guild.categories, name = '💰 RSPS Trade 💰')
    channelids = []
    for channel in category1.channels + category2.channels:
        channelids.append(channel.id)
    if channel.id in channelids and payload.emoji.id == 676988116451590226 and user.id != 479862852895899649:
        openchannel = getvalue(user.id, 'openchannel')
        if openchannel == 0:
            category = (client.get_channel(698306053590351872)).category
            newChannel = await channel.guild.create_text_channel(channel.name + ' ' + str(user)[:-5], category=category)
            await newChannel.set_permissions(user, read_messages=True, send_messages=True, read_message_history=True)
            c.execute("UPDATE rsmoney SET openchannel={} WHERE id={}".format(newChannel.id, user.id))
            embed = discord.Embed(description='<@' + str(user.id) + '>, this is your temporary private channel. You or a staff member can use `!close` when you are done to delete the channel.', color=11854069)
            embed.set_author(name='Private Channel Info', icon_url=channel.guild.icon_url)
            embed.set_footer(text='Channel Opened On: ' + str(datetime.datetime.now())[:-7])
            await newChannel.send(embed=embed)
        else:
            sent = await channel.send('<@' + str(user.id) + '>, you can only have *one* private channel at a time!')
            await asyncio.sleep(3)
            await sent.delete()

@client.event
async def on_reaction_remove(reaction, user):
    None

@client.event
async def on_message(message):
    global meleduel, magicduel
   
    message.content = message.content.lower()

    #######################################
    if message.content.startswith('!input'):
        print(message.content)
    #######################################
    elif message.content == '!log':
        if str(message.author.id) == 199630284906430465:
            await message.channel.send('Goodbye!')
            await client.logout()
    #######################################
    elif message.content.startswith('!say'):
        await message.channel.send(str(message.content[5:]))
    #######################################
    elif message.content.startswith('!emoji'):
        if isstaff(message.author.roles) == 'verified':
            try:
                await message.delete()
            except:
                print('No permissions to delete messages. RIP')
            finalmessage = ''
            characters = []
            characters += str(message.content).lower()[7:]
            for i in characters:
                if i == ' ':
                    finalmessage += ':white_small_square: '
                elif i in 'abcdefghijklmnopqrstuvwxyz':
                    finalmessage += (':regional_indicator_' + i) + ': '
                elif i == '!':
                    finalmessage += ':grey_exclamation: '
            await message.channel.send(finalmessage)
        else:
            await message.channel.send("Admin Command Only")
    #######################################
    elif message.content.startswith('!poll'):
        message.content = message.content.title()
        embed = discord.Embed(description='Respond below with 👍 for YES, 👎 for NO, or 🤔 for UNSURE/NEUTRAL', color=16724721)
        embed.set_author(name=str(message.content[6:]), icon_url=message.guild.icon_url)
        embed.set_footer(text='Polled on: ' + str(datetime.datetime.now())[:(- 7)])
        sent = await message.channel.send(embed=embed)
        await sent.add_reaction('👍')
        await sent.add_reaction('👎')
        await sent.add_reaction('🤔')
    #######################################
    elif message.content.startswith('$userinfo'):
        try:
            int(str(message.content[12:13]))
            member = message.guild.get_member(int(message.content[12:30]))
        except:
            member = message.guild.get_member(int(message.content[13:31]))
        
        roles = []
        
        for i in member.roles:
            if str(i) == '@everyone':
                roles.append('Everyone')
            else:
                roles.append(i.name)
        
        embed = discord.Embed(description=" Name: "+str(member)+"\n"+
                                            "\nRoles: "+', '.join(roles)+"\n"+
                                            "\nJoined server on: "+str(member.joined_at).split(" ")[0]+"\n"+
                                            "\nCreated account on: "+str(member.created_at).split(" ")[0]+"\n"+
                                            "\nPlaying: "+str(member.activity)+"\n", color=8270499)
        embed.set_author(name='Information of ' + str(member)[:(- 5)], icon_url=str(member.avatar_url))
        embed.set_footer(text="Spying on people's information isn't very nice...")
        await message.channel.send(embed=embed)
    #######################################













    #######################################
    elif (message.content == '!wallet') or (message.content == '!w') or (message.content == '!$'):
        for i in currencies.currencies:
            i[0] = getvalue(message.author.id, i[1])

        if any(x[0] >= 1_000_000 for x in currencies.currencies):
            sidecolor = 2693614
        elif any(x[0] >= 10_000 for x in currencies.currencies):
            sidecolor = 2490163
        else:
            sidecolor = 12249599

        embed = discord.Embed(color=sidecolor)
        embed.set_author(name=str(message.author)[:-5] + "'s Wallet", icon_url=str(message.author.avatar_url))
        embed.set_footer(text='Wallet checked on: ' + str(datetime.datetime.now())[:-7])
        
        for i in currencies.currencies:
            i[0] = formatfromk(i[0])
            if i[0] == '0k':
                i[0] = '0 k'
            if i[1] == 'osrs':
                i[1] = '07'
            embed.add_field(name=i[1].title(), value=i[0], inline=True)
        
        await message.channel.send(embed=embed)

    elif message.content.startswith('!wallet <@') or message.content.startswith('!w <@') or message.content.startswith('!$ <@'):
        try:
            int(str(message.content).split(' ')[1][2:3])
            member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
        except:
            member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
        
        for i in currencies.currencies:
            i[0] = getvalue(member.id, i[1])

        if any(x[0] >= 1_000_000 for x in currencies.currencies):
            sidecolor = 2693614
        elif any(x[0] >= 10_000 for x in currencies.currencies):
            sidecolor = 2490163
        else:
            sidecolor = 12249599

        embed = discord.Embed(color=sidecolor)
        embed.set_author(name=str(member)[:-5] + "'s Wallet", icon_url=str(member.avatar_url))
        embed.set_footer(text='Wallet checked on: ' + str(datetime.datetime.now())[:-7])
        
        for i in currencies.currencies:
            i[0] = formatfromk(i[0])
            if i[0] == '0k':
                i[0] = '0 k'
            if i[1] == 'osrs':
                i[1] = '07'
            embed.add_field(name=i[1].title(), value=i[0], inline=True)
        
        await message.channel.send(embed=embed)    
    #######################################
    elif message.content == '!privacy on':
        c.execute('UPDATE rsmoney SET privacy=True WHERE id={}'.format(message.author.id))
        embed = discord.Embed(description=('<@' + str(message.author.id)) + ">'s wallet privacy is now enabled.", color=5174318)
        embed.set_author(name='Privacy Mode', icon_url=str(message.author.avatar_url))
        await message.channel.send(embed=embed)
    
    elif message.content == '!privacy off':
        c.execute('UPDATE rsmoney SET privacy=False WHERE id={}'.format(message.author.id))
        embed = discord.Embed(description=('<@' + str(message.author.id)) + ">'s wallet privacy is now disabled.", color=5174318)
        embed.set_author(name='Privacy Mode', icon_url=str(message.author.avatar_url))
        await message.channel.send(embed=embed)
    #######################################
    elif message.content.startswith('!reset'):
        try:
            if isstaff(message.author.roles) == 'verified':
                try:
                    int(str(message.content).split(' ')[1][2:3])
                    member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
                except:
                    member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
                currency = (message.content).split(' ')[2]
                c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, 0, member.id))
                await message.channel.send('<@' + str(member.id) + ">'s **" + currency.title() + "** balance has been reset to 0.")
            else:
                await message.channel.send('Admin Command Only!')
        except:
            await message.channel.send('An **error** occurred. Make sure you use `!reset (@USER) (CURRENCY)`')
    #######################################
    elif message.content.startswith('!update'):
        try:
            if isstaff(message.author.roles) == 'verified':
                try:
                    int(str(message.content).split(' ')[1][2:3])
                    member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
                except:
                    member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
                amount = formatok(str(message.content).split(' ')[2])
                currency = (message.content).split(' ')[3]
                update_money(member.id, currency, amount)
                embed = discord.Embed(description='<@' + str(member.id) + ">'s **" + currency.title() + "** balance has been updated.", color=5174318)
                embed.set_author(name='Update Request', icon_url=str(member.avatar_url))
                await message.channel.send(embed=embed)
            else:
                await message.channel.send('Admin Command Only!')
        except:
            await message.channel.send('An **error** has occurred. Make sure you use `!update (@USER) (AMOUNT) (CURRENCY)`.')
    #######################################
    elif message.content.startswith('!help') or message.content.startswith('!commands'):
        embed = discord.Embed(description=  #"\n `!colorpicker` - Shows a random color\n" +
                                            #"\n `!emoji (WORDS)` - The bot sends back those words in emoji form\n" +
                                            #"\n `!start unscramble` - Starts a game where you unscramble a word\n" +
                                            #"\n `!start hangman` - Starts a game of hangman\n" +
                                            #"\n `!random (singleplayer or multiplayer) (SIZE)` - Starts a game where you guess a number between 1 and the given size\n" +
                                            #"\n `!poll (QUESTION)` - Starts a Yes/No poll with the given question\n" +
                                            "\n `!w`, `!wallet`, `!$`, or `!tokens` - Checks your own tokens\n" +
                                            "\n `!w (@USER)`, `!wallet (@USER)`, `!$ (@USER)`, or `!tokens (@USER)` - Checks that user's tokens\n" +
                                            #"\n `!daily` - Gives 800 tokens each day\n" +
                                            # "\n `!swap (rs3 or 07) (AMOUNT)` - Swaps that amount of gold to the other game" +
                                            # "\n `!rates` - Shows the swapping rates between currencies" +
                                            "\n `!flower (AMOUNT) (hot, cold, red, orange, yellow, green, blue, or purple)` - Hot or cold gives x2 minus commission, specific color gives x6 minus commission\n" +
                                            #"\n `!cashin (rs3 or 07) (AMOUNT)` - Notifies a cashier that you want to cash in that amount\n" +
                                            #"\n `!cashout (rs3 or 07) (AMOUNT)` - Notifies a cashier that you want to cash out that amount\n" +
                                            #"\n `!wager`, `!total bet`, or `!tb` - Shows the total amount of tokens you've bet\n" +
                                            "\n `!ddsstake (AMOUNT)` - Hosts a mele duel betting that amount of tokens\n" +
                                            "\n `!magebox (AMOUNT)` - Hosts a magic duel betting that amount of tokens\n", color=2513759)
                                            #"\n `!transfer (@USER) (AMOUNT)` - Transfers that amount of tokens from your wallet to the user's wallet\n"
        embed.set_author(name='CryptoScape Bot Commands', icon_url=str(message.guild.icon_url))
        await message.channel.send(embed=embed)
    #######################################
    elif message.content.lower().startswith('!transfer'):
        try:
            transfered = formatok(str(message.content).split(' ')[2])
            currency = (message.content).split(' ')[3]
            current = getvalue(message.author.id, currency)
            if transfered >= 1:
                if current >= transfered:
                    try:
                        int(str(message.content).split(' ')[1][2:3])
                        member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
                    except:
                        member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
                    taker = getvalue(member.id, currency)
                    c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, current - transfered, message.author.id))
                    c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, taker + transfered, member.id))
                    await message.channel.send('<@' + str(message.author.id) + '> has transfered **' + formatfromk(transfered) + ' ' + currency.title() + '** to <@' + str(member.id) + ">'s wallet.")
                else:
                    await message.channel.send('<@' + str(message.author.id) + ">, You don't have enough money to transfer that amount!")
            else:
                await message.channel.send('You must transfer at least **1** unit of currency.')
        except:
            await message.channel.send('An **error** has occurred. Make sure you use `!transfer (@USER) (AMOUNT) (CURRENCY)`.')
    #######################################
    elif message.content == '!close':
        if message.channel.category.id == 698305020617031742:
            c.execute("UPDATE rsmoney SET openchannel={} WHERE openchannel={}".format(0, message.channel.id))
            await message.channel.delete()
    #######################################
    elif message.content.startswith('message'):
        channel = client.get_channel(int((message.content).split(' ')[1]))
        embed = discord.Embed(description='React to this message with <:crytoscapelogo:676988116451590226> to create a **private room**.', color=11854069)
        embed.set_author(name=(channel.name).title() + ' Ticket', icon_url=message.guild.icon_url)
        sent = await channel.send(embed=embed)
        await sent.add_reaction(client.get_emoji(676988116451590226))
    #######################################
    elif message.content.startswith('!53') or message.content.startswith('!50') or message.content.startswith('!75') or message.content.startswith('!95'):
        if message.channel.id in [701470129942429697, 700186111422627870]:
            #try:
            currency = str(message.content).split(' ')[2]
            bet = formatok(str(message.content).split(' ')[1])
            current = getvalue(message.author.id, currency)
            
            if isenough(bet, currency)[0]:
                if message.content.startswith('!53x2') or message.content.startswith('!53'):
                    (title, odds, multiplier) = ('53x2', 54, 2)
                elif message.content.startswith('!50x1.8') or message.content.startswith('!50'):
                    (title, odds, multiplier) = ('50x1.8', 51, 1.8)
                elif message.content.startswith('!75x3') or message.content.startswith('!75'):
                    (title, odds, multiplier) = ('75x3', 76, 3)
                elif message.content.startswith('!95x7') or message.content.startswith('!95'):
                    (title, odds, multiplier) = ('95x7', 96, 7)
                
                if current >= bet:
                    #getrandint(id)
                    roll = random.randint(1, 100)
                    
                    if roll in range(1, odds):
                        winnings = bet
                        words = 'Rolled **' + str(roll) + '** out of **100**. You lost **' + formatfromk(bet) + '** ' + currency.title() + '.'
                        (sidecolor, gains, win) = (16718121, bet * -1, False)
                    else:
                        winnings = formatfromk(int(bet * multiplier))
                        words = 'Rolled **' + str(roll) + '** out of **100**. You won **' + str(winnings) + '** ' + currency.title() + '.'
                        winnings = formatok(winnings)
                        (sidecolor, gains, win) = (3997475, (bet * multiplier) - bet, True)
                    
                    update_money(int(message.author.id), gains, currency)
                    # c.execute('SELECT nonce FROM data')
                    # nonce = int(c.fetchone()[0])
                    # clientseed = getvalue(message.author.id, 'clientseed', 'rsmoney')
                    embed = discord.Embed(color=sidecolor)
                    embed.set_author(name=str(message.author), icon_url=str(message.author.avatar_url))
                    embed.add_field(name=title, value=words, inline=True)
                    # embed.set_footer(text=((('Nonce: ' + str(nonce - 1)) + ' | Client Seed: "') + str(clientseed)) + '"')
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(('<@' + str(message.author.id)) + ">, you don't have that much gold!")
            else:
                await message.channel.send(isenough(bet, currency)[1])
            #except:
            #    await message.channel.send('An **error** has occurred. Make sure you use `!(50, 53, 75, or 95) (BET) (CURRENCY)`.')
        else:
            await message.channel.send('This command can only be used in one of the dicing channels.')
    # elif message.content.startswith('!flower'):
    #     try:
    #         enough = True
    #         bet = formatok(message.content.split(' ')[1])
    #         current = getvalue(int(message.author.id), 'tokens')
    #         totaltokens = getvalue(int(message.author.id), 'tokens')
    #         index = random.randint(0, 5)
    #         flower = flowers[index]
    #         sidecolor = sidecolors[index]
    #         commission = 0.05
    #         if bet < 100:
    #             await message.channel.send('The minimum amount you can bet is **100** tokens.')
    #             enough = False
    #         if enough == True:
    #             if current >= bet:
    #                 win = False
    #                 if message.content.split(' ')[2] == 'hot':
    #                     if (flower == 'Red') or (flower == 'Orange') or (flower == 'Yellow'):
    #                         multiplier = 2
    #                         win = True
    #                     else:
    #                         multiplier = 0
    #                 elif message.content.split(' ')[2] == 'cold':
    #                     if (flower == 'Blue') or (flower == 'Green') or (flower == 'Purple'):
    #                         multiplier = 2
    #                         win = True
    #                     else:
    #                         multiplier = 0
    #                 elif message.content.split(' ')[2].title() in flowers:
    #                     if flower == message.content.split(' ')[2].title():
    #                         multiplier = 6
    #                         win = True
    #                     else:
    #                         multiplier = 0
    #                 winnings = (bet * multiplier) - ((commission * bet) * multiplier)
    #                 if isinstance(winnings, float):
    #                     if winnings.is_integer():
    #                         winnings = int(winnings)
    #                 if win == True:
    #                     words = ((((('Congratulations! The color of the flower was `' + flower) + '`. ') + str(message.author)) + ' won `') + '{:,}'.format(winnings)) + '` tokens.'
    #                     if multiplier == 2:
    #                         update_money(int(message.author.id), bet - ((bet * commission) * multiplier))
    #                     else:
    #                         update_money(int(message.author.id), (bet * multiplier) - ((bet * commission) * multiplier))
    #                 else:
    #                     words = ((((('Sorry, the color the flower was `' + flower) + '`. ') + str(message.author)) + ' lost `') + '{:,}'.format(bet)) + '` tokens.'
    #                     update_money(int(message.author.id), bet * (- 1))
    #                 c.execute('UPDATE rsmoney SET tokenstotal={} WHERE id={}'.format(totaltokens + bet, message.author.id))
    #                 embed = discord.Embed(description=words, color=sidecolor)
    #                 embed.set_author(name=str(message.author)[:(- 5)] + "'s Gamble", icon_url=str(message.author.avatar_url))
    #                 embed.set_footer(text='Gambled on: ' + str(datetime.datetime.now())[:(- 7)])
    #                 await message.channel.send(embed=embed)
    #             else:
    #                 await message.channel.send(('<@' + str(message.author.id)) + ">, You don't have that many tokens!")
    #         else:
    #             None
    #     except:
    #         await message.channel.send('An **error** has occurred. Make sure you use `!flower (Amount) (hot, cold, red, orange, yellow, green, blue, or purple)`.')
    #######################################
    elif message.content.startswith('!ddsstake'):
        if meleduel:
            await message.channel.send('There is a mele duel already going on. Please wait until that one finishes.')
        else:
            currency = (message.content).split(' ')[2]
            melecurrent = getvalue(message.author.id, currency)
            melebet = formatok(message.content.split(' ')[1])

            if isenough(melebet, currency):
                meleduel = True
                c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, melecurrent - melebet, message.author.id))
                await message.channel.send('<@' + str(message.author.id) + '> wants to duel for ' + formatfromk(melebet) + ' ' + currency + '. Use `!call` to accept the duel.')
                while True:
                    call = await client.wait_for('message', timeout=60)

                    if call is None:
                        await message.channel.send('<@' + str(message.author.id) + ">'s duel request has timed out.")
                        c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, melecurrent, message.author.id))
                        meleduel = False
                        break

                    melecaller = call.author

                    if str(melecaller.id) == str(message.author.id):
                        await message.channel.send('As exciting as it may sound, you cannot duel yourself ._.')
                        continue

                    meleCallerCurrent = getvalue(melecaller.id, currency)

                    if meleCallerCurrent < melebet:
                        await message.channel.send("You don't have enough tokens to call that duel.")
                        continue
                    else:
                        c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, meleCallerCurrent - melebet, melecaller.id))
                        break

                if meleduel:
                    melegambler = [message.author, 99, 5, 4, False, 0, 4, 0]
                    melecaller = [melecaller, 99, 5, 4, False, 0, 4, 0]
                    meleplayers = [melegambler, melecaller]
                    melewinner = None
                    while True:
                        if melewinner == None:
                            melesent = await message.channel.send(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                            for i in meleplayers:
                                if melewinner != None:
                                    break
                                else:
                                    meleopponent = meleplayers[int(meleplayers.index(i)) - 1]
                                    if i[3] < 4:
                                        i[7] += 1
                                        if (i[7] % 4) == 0:
                                            i[3] += 1
                                            await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                    if i[4]:
                                        i[5] += 1
                                        if (i[5] % 4) == 0:
                                            i[1] -= i[6]
                                            await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                            await message.channel.send(str(i[0]) + ' took ' + str(i[6]) + ' damage from poison.')
                                    await message.channel.send(str(i[0]) + ', it is your turn. Use `!rocktail`, `!dds` or `!whip`.')
                                    while True:
                                        move = await client.wait_for('message', timeout=20)
                                        if move is None:
                                            whip = get(client.emojis, name='whip')
                                            await message.channel.send('Took too long. Automatically used ' + str(whip) + '.')
                                            hit = random.randint(0, 27)
                                            meleopponent[1] -= hit
                                            if meleopponent[1] < 0:
                                                meleopponent[1] = 0
                                            await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                            await message.channel.send(str(i[0]) + ' has hit ' + str(meleopponent[0]) + ' with their ' + str(whip) + ' and dealt ' + str(hit) + ' damage.')
                                            if meleopponent[1] < 1:
                                                melewinner = i
                                            break
                                        if str(move.content).lower() == '!rocktail':
                                            rocktail = get(client.emojis, name='rocktail')
                                            if i[2] < 1:
                                                await message.channel.send('You are out of ' + str(rocktail) + '. Please use `!dds` or `!whip`.')
                                                continue
                                            else:
                                                healing = random.randint(22, 29)
                                                i[2] -= 1
                                                i[1] += healing
                                                if i[1] > 99:
                                                    i[1] = 99
                                                await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                                await message.channel.send(str(i[0]) + ' eats a ' + str(rocktail) + ' and heals ' + str(healing) + ' hp.')
                                                break
                                        elif str(move.content).lower() == '!dds':
                                            dds = get(client.emojis, name='dds')
                                            if i[3] < 1:
                                                await message.channel.send('You are out of ' + str(dds) + ' specs. Please use `!rocktail` or `!whip`.')
                                                continue
                                            else:
                                                i[3] -= 1
                                                hit = random.randint(0, 20) + random.randint(0, 20)
                                                meleopponent[1] -= hit
                                                if meleopponent[1] < 0:
                                                    meleopponent[1] = 0
                                                await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                                await message.channel.send(str(i[0]) + ' has used a ' + str(dds) + ' on ' + str(meleopponent[0]) + ' and dealt ' + str(hit) + ' damage.')
                                                if meleopponent[1] < 1:
                                                    winner = i
                                                elif random.randint(1, 4) == 4:
                                                    meleopponent[4] = True
                                                    meleopponent[6] = 4
                                                    await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                                    await message.channel.send(str(meleopponent[0]) + ' has been poisoned by the ' + str(dds) + '!')
                                                break
                                        elif str(move.content).lower() == '!whip':
                                            hit = random.randint(0, 27)
                                            meleopponent[1] -= hit
                                            await melesent.edit(embed=hpupdate(meleplayers, str(message.guild.icon_url), 'mele'))
                                            whip = get(client.emojis, name='whip')
                                            await message.channel.send(str(i[0]) + ' has hit ' + str(meleopponent[0]) + ' with their ' + str(whip) + ' and dealt ' + str(hit) + ' damage.')
                                            if meleopponent[1] < 1:
                                                melewinner = i
                                            break
                                        else:
                                            await message.channel.send('An **error** has occured. Make sure to use `!rocktail` `!dds` or `!whip`.')
                                            continue
                        else:
                            winnert = getvalue(int(winner[0].id), currency)
                            c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, winnert + (melebet * 2), winner[0].id))
                            await message.channel.send('<@' + str(melewinner[0].id) + '> Has won the duel and gained **' + formatfromk(melebet * 2) + ' ' + currency + '**!')
                            meleduel = False
                            melewinner = None
                            break
                else:
                    None
            else:
                await message.channel.send(isenough(bet, currency)[1])
    #######################################
    # elif message.content.startswith('!magebox'):
    #     #try:
    #     if magicduel:
    #         await message.channel.send('There is a magic duel already going on. Please wait until that one finishes.')
    #     else:
    #         enough = True
    #         magiccurrent = getvalue(int(message.author.id), 'tokens')
    #         magicbet = formatok(message.content.split(' ')[1])
    #         if magicbet < 100:
    #             await message.channel.send('The minimum amount you can bet is **100** tokens.')
    #             enough = False
    #         if enough:
    #             magicduel = True
    #             c.execute('UPDATE rsmoney SET tokens={} WHERE id={}'.format(magiccurrent - magicbet, message.author.id))
    #             await message.channel.send(((('<@' + str(message.author.id)) + '> wants to duel for ') + '{:,}'.format(magicbet)) + ' tokens. Use `!call` to accept the duel.')
    #             while True:
    #                 call = await client.wait_for('message', timeout=60)
    #                 if call is None:
    #                     await message.channel.send(('<@' + str(message.author.id)) + ">'s duel request has timed out.")
    #                     c.execute('UPDATE rsmoney SET tokens={} WHERE id={}'.format(magiccurrent, message.author.id))
    #                     magicduel = False
    #                     break
    #                 magiccaller = call.author
    #                 if str(magiccaller.id) == str(message.author.id):
    #                     await message.channel.send('As exciting as it may sound, you cannot duel yourself ._.')
    #                     continue
    #                 magiccallertokens = getvalue(int(magiccaller.id), 'tokens')
    #                 if magiccallertokens < magicbet:
    #                     await message.channel.send("You don't have enough tokens to call that duel.")
    #                     continue
    #                 else:
    #                     c.execute('UPDATE rsmoney SET tokens={} WHERE id={}'.format(magiccallertokens - magicbet, magiccaller.id))
    #                     break
    #             if magicduel:
    #                 magicgambler = [message.author, 99, 5, False]
    #                 magiccaller = [magiccaller, 99, 5, False]
    #                 magicplayers = [magicgambler, magiccaller]
    #                 magicwinner = None
    #                 while True:
    #                     if magicwinner == None:
    #                         magicsent = await message.channel.send(embed=hpupdate(magicplayers, str(message.guild.icon_url), 'magic'))
    #                         for i in magicplayers:
    #                             if magicwinner != None:
    #                                 break
    #                             else:
    #                                 if i[3] == True:
    #                                     await message.channel.send(str(i[0]) + ' is frozen and cannot do anything this turn.')
    #                                     i[3] = False
    #                                     continue
    #                                 magicopponent = magicplayers[int(magicplayers.index(i)) - 1]
    #                                 await message.channel.send(str(i[0]) + ', it is your turn. Use `!rocktail`, `!blood` or `!ice`.')
    #                                 while True:
    #                                     move = await client.wait_for('message', timeout=20)
    #                                     if move is None:
    #                                         blood = get(
    #                                         client.emojis, name='blood')
    #                                         await message.channel.send(('Took too long. Automatically used ' + str(blood)) + '.')
    #                                         hit = random.randint(0, 29)
    #                                         magicopponent[1] -= hit
    #                                         if magicopponent[1] < 0:
    #                                             magicopponent[1] = 0
    #                                         healed = int(hit * 0.25)
    #                                         i[1] += healed
    #                                         if i[1] > 99:
    #                                             i[1] = 99
    #                                         await magicsent.edit(embed=hpupdate(magicplayers, str(message.guild.icon_url), 'magic'))
    #                                         blood = get(
    #                                         client.emojis, name='blood')
    #                                         await message.channel.send(((((((((str(i[0]) + ' has used ') + str(blood)) + ' on ') + str(magicopponent[0])) + ', dealt ') + str(hit)) + ' damage, and was healed for ') + str(healed)) + ' HP.')
    #                                         if magicopponent[1] < 1:
    #                                             magicwinner = i
    #                                         break
    #                                     if str(move.content).lower() == '!rocktail':
    #                                         if i[2] < 1:
    #                                             rocktail = get(
    #                                             client.emojis, name='rocktail')
    #                                             await message.channel.send(('You are out of ' + str(rocktail)) + '. Please use `!blood` or `!ice`.')
    #                                             continue
    #                                         else:
    #                                             healing = random.randint(22, 29)
    #                                             i[2] -= 1
    #                                             i[1] += healing
    #                                             if i[1] > 99:
    #                                                 i[1] = 99
    #                                             await magicsent.edit(embed=hpupdate(magicplayers, str(message.guild.icon_url), 'magic'))
    #                                             rocktail = get(
    #                                             client.emojis, name='rocktail')
    #                                             await message.channel.send(((((str(i[0]) + ' eats a ') + str(rocktail)) + ' and heals ') + str(healing)) + ' hp.')
    #                                             break
    #                                     elif str(move.content).lower() == '!ice':
    #                                         hit = random.randint(0, 30)
    #                                         magicopponent[1] -= hit
    #                                         if magicopponent[1] < 0:
    #                                             magicopponent[1] = 0
    #                                         await magicsent.edit(embed=hpupdate(magicplayers, str(message.guild.icon_url), 'magic'))
    #                                         ice = get(
    #                                         client.emojis, name='ice')
    #                                         await message.channel.send(((((((str(i[0]) + ' has used ') + str(ice)) + ' on ') + str(magicopponent[0])) + ' and dealt ') + str(hit)) + ' damage.')
    #                                         if magicopponent[1] < 1:
    #                                             magicwinner = i
    #                                         elif random.randint(1, 5) == 5:
    #                                             magicopponent[3] = True
    #                                             ice = get(
    #                                             client.emojis, name='ice')
    #                                             await message.channel.send(((str(magicopponent[0]) + ' has been frozen from ') + str(ice)) + '.')
    #                                         break
    #                                     elif str(move.content).lower() == '!blood':
    #                                         hit = random.randint(0, 29)
    #                                         magicopponent[1] -= hit
    #                                         if magicopponent[1] < 0:
    #                                             magicopponent[1] = 0
    #                                         healed = int(hit * 0.25)
    #                                         i[1] += healed
    #                                         if i[1] > 99:
    #                                             i[1] = 99
    #                                         await magicsent.edit(embed=hpupdate(magicplayers, str(message.guild.icon_url), 'magic'))
    #                                         blood = get(
    #                                         client.emojis, name='blood')
    #                                         await message.channel.send(((((((((str(i[0]) + ' has used ') + str(blood)) + ' on ') + str(magicopponent[0])) + ', dealt ') + str(hit)) + ' damage, and was healed for ') + str(healed)) + ' HP.')
    #                                         if magicopponent[1] < 1:
    #                                             magicwinner = i
    #                                         break
    #                                     else:
    #                                         await message.channel.send('An **error** has occured. Make sure to use `!rocktail` `!blood` or `!ice`.')
    #                                         continue
    #                     else:
    #                         winnert = getvalue(int(magicwinner[0].id), 'tokens')
    #                         c.execute('UPDATE rsmoney SET tokens={} WHERE id={}'.format((winnert + magicbet) + magicbet, magicwinner[0].id))
    #                         await message.channel.send(((('<@' + str(magicwinner[0].id)) + '> Has won the duel and gained ') + '{:,}'.format(magicbet * 2)) + ' tokens!')
    #                         magicduel = False
    #                         magicwinner = None
    #                         break
    #             else:
    #                 None
    #         else:
    #             None
    #     #except:

#website info
#total wallet
#donate system
#duel system
#more words

client.loop.create_task(my_background_task())
Bot_Token = os.environ['TOKEN']
client.run(str(Bot_Token))
#heroku pg:psql postgresql-shallow-22073 --app cscape2
#https://discordapp.com/oauth2/authorize?client_id=479862852895899649&scope=bot&permissions=0