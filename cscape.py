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
c=conn.cursor()
conn.set_session(autocommit=True)

# c.execute("DROP TABLE rsmoney")
# c.execute("""CREATE TABLE rsmoney (
# 				id bigint,
# 				tokens bigint,
# 				tokenstotal bigint
# 				)""")
# conn.commit()

client = discord.Client()


def add_member(userid,tokens,tokenstotal):
	c.execute("INSERT INTO rsmoney VALUES (%s, %s, %s)", (userid,tokens,tokenstotal))
	conn.commit()

def getvalue(userid, column):
	try:
		c.execute("SELECT tokens FROM rsmoney WHERE id={}".format(userid))
		tester=int(str(c.fetchone())[1:-2])
	except:
		add_member(int(userid),0,0)
		return 0
	c.execute("SELECT {} FROM rsmoney WHERE id={}".format(str(column),userid))
	returned=int(c.fetchone()[0])
	return returned

#amount should be in K not M
def update_money(userid,amount):
	tokens=getvalue(int(userid), "tokens")
	c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(tokens+amount, userid))
	conn.commit()

def reset():
	global guesses,solved,blank,wrong,word1
	guesses=6
	solved=[]
	blank=[]
	wrong=[]
	word1="placeholderplaceholderplaceholderplaceholder"

def isstaff(checkedid,serverroles,authorroles):
	for i in open("staff.txt"):
		client.get_guild(550630947767320578)
		role=get(serverroles, name=str(i.strip()))
		if role in authorroles:
			return "verified"

def formatok(amount):
	#takes amount as string from message.content
	#returns an integer
	if (amount[-1:]).lower()=="m":
		return int(float(str(amount[:-1]))*1000000)
	elif (amount[-1:]).lower()=="k":
		return int(float(str(amount[:-1]))*1000)
	elif (amount[-1:]).lower()=="b":
		return int(float(str(amount[:-1]))*1000000000)
	else:
		return int(amount)

def hpupdate(players, url, dueltype):

	embed = discord.Embed(color=16766463)
	embed.set_author(name="Fight to the Death!", icon_url=url)
	for i in players:
		hp=int(i[1])
		if hp in range(76,100):
			hp = get(client.get_all_emojis(), name='hpbar100')
		elif hp in range(51, 76):
			hp = get(client.get_all_emojis(), name='hpbar75')
		elif hp in range(26, 51):
			hp = get(client.get_all_emojis(), name='hpbar50')
		elif hp in range(1,26):
			hp = get(client.get_all_emojis(), name='hpbar25')
		elif hp<1:
			hp = get(client.get_all_emojis(), name='hpbar0')
		rocktail = get(client.get_all_emojis(), name='rocktail')

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

######################################################################################

#Predefined Variables
colors=["A","B","C","D","E","F","0","1","2","3","4","5","6","7","8","9"]
objects=[]
flowers=["Red","Orange","Yellow","Green","Blue","Purple"]
sidecolors=[16711680, 16743712, 16776960, 1305146, 1275391, 16730111]
blank=[]
meleduel=False
magicduel=False

async def my_background_task():
	await client.wait_until_ready()
	while not client.is_closed:
		None
		await asyncio.sleep(600)


@client.event
async def on_ready():
	print("Bot Logged In!");

@client.event
async def on_message_delete(message):
	None

@client.event
async def on_message(message):
	global objects,word,answer,word1,guesses,solved,blank,wrong,meleduel,magicduel
	
	message.content=message.content.lower()

	#############################################
	if message.content.startswith("!input"):
		print(message.content)
    ###########################################
	elif message.content==("!log"):
		if str(message.author.id)==("199630284906430465"):
			await client.send_message(message.channel, "Goodbye!")
			await client.logout()
	#########################################
	elif message.content.startswith("!say"):
		await client.send_message(message.channel, str(message.content[5:]))
	####################################################
	elif message.content.startswith("!emoji"):
		if isstaff(message.author.id)=="verified":
			try:
				await client.delete_message(message)
			except:
				print("No permissions to delete messages. RIP")
			finalmessage=("")
			characters=[]
			characters+=(str(message.content).lower())[7:]
			for i in characters:
				if i==" ":
					finalmessage+=":white_small_square: "
				elif i in "abcdefghijklmnopqrstuvwxyz":
					finalmessage+=":regional_indicator_"+i+": "
				elif i=="!":
					finalmessage+=":grey_exclamation: "
			await client.send_message(message.channel, finalmessage)
		else:
			await client.send_message(message.channel, "DON'T TOUCHA MY SPAGHET!")
	############################################
	elif message.content.startswith("!poll"):
		message.content=(message.content).title()
		embed = discord.Embed(description="Respond below with 👍 for YES, 👎 for NO, or 🤔 for UNSURE/NEUTRAL", color=16724721)
		embed.set_author(name=str(message.content[6:]), icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
		embed.set_footer(text="Polled on: "+str(datetime.datetime.now())[:-7])
		sent = await client.send_message(message.channel, embed=embed)
		await client.add_reaction(sent,"👍")
		await client.add_reaction(sent,"👎")
		await client.add_reaction(sent,"🤔")
	#############################################
	elif message.content.startswith("!userinfo"):
		try:
			int(str(message.content[12:13]))
			member=message.server.get_member(message.content[12:30])
		except:
			member=message.server.get_member(message.content[13:31])
		roles=[]
		for i in member.roles:
			if str(i)=="@everyone":
				roles.append("everyone")
			else:
				roles.append(i.name)
		embed = discord.Embed(description=" `Name:` "+str(member)+"\n"+
											"\n`ID:` "+str(member.id)+
											"\n\n`Roles:` "+', '.join(roles)+
											"\n\n`Joined server on:` "+str(member.joined_at).split(" ")[0]+
											"\n\n`Created account on:` "+str(member.created_at).split(" ")[0]+
											"\n\n`Playing:` "+str(member.game)+"\n", color=8270499)
		embed.set_author(name="Information of "+str(member)[:-5], icon_url=str(member.avatar_url))
		embed.set_footer(text="Spying on people's information isn't very nice...")
		await client.send_message(message.channel, embed=embed)
	##############################################
	















	###################################################
	elif (message.content)==("!wallet") or (message.content)==("!w") or message.content=="!$" or (message.content)=="!tokens":
		tokens=getvalue(int(message.author.id), "tokens")
		if tokens>=1000000:
			sidecolor=2693614
		elif tokens>=100000:
			sidecolor=2490163
		else:
			sidecolor=12249599

		tokens="{:,}".format(tokens)

		embed = discord.Embed(color=sidecolor)
		embed.set_author(name=(str(message.author))[:-5]+"'s Wallet", icon_url=str(message.author.avatar_url))
		embed.add_field(name="Tokens", value=tokens, inline=True)
		embed.set_footer(text="Wallet checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)



	elif  (message.content).startswith("!wallet <@") or (message.content).startswith("!w <@") or message.content.startswith("!$ <@") or message.content.startswith("!tokens <@"):
		if message.content.startswith("!wallet <@"):
			try:
				int(str(message.content[10:11]))
				member=message.server.get_member(message.content[10:28])
			except:
				member=message.server.get_member(message.content[11:29])
		else:
			try:
				int(str(message.content[5:6]))
				member=message.server.get_member(message.content[5:23])
			except:
				member=message.server.get_member(message.content[6:24])
		
		tokens=getvalue(int(member.id), "tokens")

		if tokens>=1000000:
			sidecolor=2693614
		elif tokens>=100000:
			sidecolor=2490163
		else:
			sidecolor=12249599

		tokens="{:,}".format(tokens)

		embed = discord.Embed(color=sidecolor)
		embed.set_author(name=(str(member))[:-5]+"'s Wallet", icon_url=str(member.avatar_url))
		embed.add_field(name="Tokens", value=tokens, inline=True)
		embed.set_footer(text="Wallet checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	##########################################
	elif message.content.startswith("!reset"):
		try:
			if isstaff(message.author.id)=="verified":
				try:
					int(str(message.content).split(" ")[1][2:3])
					member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
				except:
					member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

				c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(0, int(member.id)))
				conn.commit()

				await client.send_message(message.channel, str(member)+"'s tokens have been reset to 0. RIP")
			else:
				await client.send_message(message.channel, "Admin Command Only!")
		except:
			await client.send_message(message.channel, "An **error** occurred. Make sure you use `!reset (@user)`")
	###########################################
	elif ((message.content).lower()).startswith("!update"):
		try:
			if isstaff(message.author.id)=="verified":
				amount=formatok(str(message.content).split(" ")[2])

				try:
					int(str(message.content).split(" ")[1][2:3])
					member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
				except:
					member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

				update_money(int(member.id), amount)
				member=message.server.get_member(str(member.id))
				await client.send_message(message.channel, str(member)+"'s tokens have been updated.")

			else:
				await client.send_message(message.channel, "Admin Command Only!")
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!update (@user) (amount)`.")
	#############################################
	elif message.content.startswith("!help") or message.content.startswith("!commands"):
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

		embed.set_author(name="CryptoScape Bot Commands", icon_url=str(message.server.icon_url))
		await client.send_message(message.channel, embed=embed)
	###################################
	elif ((message.content).lower()).startswith("!transfer"):
		try:
			transfered=formatok(str(message.content).split(" ")[2])
			enough=True

			if transfered<1:
				await client.send_message(message.channel, "You must transfer at least **1** token.")
				enough=False

			current=getvalue(int(message.author.id), "tokens")

			if enough==True:
				if current>=transfered:
					try:
						int(str(message.content).split(" ")[1][2:3])
						member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
					except:
						member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

					taker=getvalue(int(member.id), "tokens")

					c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(current-transfered, message.author.id))
					c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(taker+transfered, member.id))
					conn.commit()

					await client.send_message(message.channel, "<@"+str(message.author.id)+"> has transfered "+"{:,}".format(transfered)+" tokens to <@"+str(member.id)+">'s wallet.")
				else:
					await client.send_message(message.channel, "<@"+str(message.author.id)+">, You don't have enough tokens to transfer that amount!")
			else:
				None
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!transfer (@user) (Amount you want to give)`.")
	################################
	elif message.content.startswith("!flower"):
		try:
			enough=True
			bet=formatok((message.content).split(" ")[1])
			current=getvalue(int(message.author.id), "tokens")
			totaltokens=getvalue(int(message.author.id), "tokens")
			index=random.randint(0,5)
			flower=flowers[index]
			sidecolor=sidecolors[index]
			commission=0.05

			if bet<100:
				await client.send_message(message.channel, "The minimum amount you can bet is **100** tokens.")
				enough=False

			if enough==True:	
				if current>=bet:
					win=False
					if (message.content).split(" ")[2]=="hot":
						if flower=="Red" or flower=="Orange" or flower=="Yellow":
							multiplier=2
							win=True
						else:
							multiplier=0
					elif (message.content).split(" ")[2]=="cold":
						if flower=="Blue" or flower=="Green" or flower=="Purple":
							multiplier=2
							win=True
						else:
							multiplier=0
					elif ((message.content).split(" ")[2]).title() in flowers:
						if flower==((message.content).split(" ")[2]).title():
							multiplier=6
							win=True
						else:
							multiplier=0

					winnings=(bet*multiplier)-(commission*bet*multiplier)
					if isinstance(winnings, float):
						if (winnings).is_integer():
							winnings=int(winnings)

					if win==True:
						words=("Congratulations! The color of the flower was `"+flower+"`. "+str(message.author)+" won `"+"{:,}".format(winnings)+"` tokens.")
						if multiplier==2:
							update_money(int(message.author.id), (bet)-(bet*commission*multiplier))
						else:
							update_money(int(message.author.id), (bet*multiplier)-(bet*commission*multiplier))
					else:
						words=("Sorry, the color the flower was `"+flower+"`. "+str(message.author)+" lost `"+"{:,}".format(bet)+"` tokens.")
						update_money(int(message.author.id), bet*-1)

					c.execute("UPDATE rsmoney SET tokenstotal={} WHERE id={}".format(totaltokens+bet, message.author.id))
					conn.commit()

					embed = discord.Embed(description=words, color=sidecolor)
					embed.set_author(name=(str(message.author))[:-5]+"'s Gamble", icon_url=str(message.author.avatar_url))
					embed.set_footer(text="Gambled on: "+str(datetime.datetime.now())[:-7])
					await client.send_message(message.channel, embed=embed)	
				else:
					await client.send_message(message.channel, "<@"+str(message.author.id)+">, You don't have that many tokens!")
			else:
				None
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!flower (Amount) (hot, cold, red, orange, yellow, green, blue, or purple)`.")
	##########################################
	elif ((message.content).lower()).startswith("!wager") or ((message.content).lower()).startswith("!total bet") or ((message.content).lower()).startswith("!tb"):
		tokens=getvalue(int(message.author.id), "tokenstotal")
		tokens="{:,}".format(tokens)
		embed = discord.Embed(color=16766463)
		embed.set_author(name=(str(message.author))[:-5]+"'s Total Bets", icon_url=str(message.author.avatar_url))
		embed.add_field(name="Total Tokens Bet", value=tokens, inline=True)
		embed.set_footer(text="Total Bets checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	########################################
	elif message.content.startswith("!ddsstake"):
		#try:
		if meleduel==True:
			await client.send_message(message.channel, "There is a mele duel already going on. Please wait until that one finishes.")
		else:
			enough=True
			melecurrent=getvalue(int(message.author.id), "tokens")
			melebet=formatok((message.content).split(" ")[1])

			if melebet<100:
				await client.send_message(message.channel, "The minimum amount you can bet is **100** tokens.")
				enough=False

			if enough:
				meleduel=True
				c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(melecurrent-melebet, message.author.id))
				await client.send_message(message.channel, "<@"+str(message.author.id)+"> wants to duel for "+'{:,}'.format(melebet)+" tokens. Use `!call` to accept the duel.")
				while True:
					call = await client.wait_for_message(timeout=60, channel=message.channel, content="!call")
					if call is None:
						await client.send_message(message.channel, "<@"+str(message.author.id)+">'s duel request has timed out.")
						c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(melecurrent, message.author.id))
						meleduel=False
						break
					melecaller=call.author
					if str(melecaller.id)==str(message.author.id):
						await client.send_message(message.channel, "As exciting as it may sound, you cannot duel yourself ._.")

						continue
					melecallertokens=getvalue(int(melecaller.id), "tokens")
					if melecallertokens<melebet:
						await client.send_message(message.channel, "You don't have enough tokens to call that duel.")
						continue
					else:
						c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(melecallertokens-melebet, melecaller.id))
						break

				if meleduel:
					#player=[member object, hp, sharks, dds specs, poisoned, turns since poisoned, poison damage, turns since speced]
					melegambler=[(message.author), 99, 5, 4, False, 0, 4, 0]
					melecaller=[melecaller, 99, 5, 4, False, 0, 4, 0]
					meleplayers=[melegambler,melecaller]
					melewinner=None
					while True:
						if melewinner==None:
							melesent = await client.send_message(message.channel, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
							for i in meleplayers:
								if melewinner!=None:
									break
								else:
									meleopponent=meleplayers[int(meleplayers.index(i))-1]
									if i[3]<4:
										i[7]+=1
										if i[7]%4==0:
											i[3]+=1
											await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
									if i[4]==True:
										i[5]+=1
										if i[5]%4==0:
											i[1]-=i[6]
											await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
											await client.send_message(message.channel, str(i[0])+" took "+str(i[6])+" damage from poison.")

									await client.send_message(message.channel, str(i[0])+", it is your turn. Use `!rocktail`, `!dds` or `!whip`.")
									while True:
										move = await client.wait_for_message(timeout=20, channel=message.channel, author=i[0])
										if move is None:
											whip = get(client.get_all_emojis(), name='whip')
											await client.send_message(message.channel, "Took too long. Automatically used "+str(whip)+".")
											hit=random.randint(0,27)
											meleopponent[1]-=hit
											if meleopponent[1]<0:
												meleopponent[1]=0
											await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
											whip = get(client.get_all_emojis(), name='whip')
											await client.send_message(message.channel, str(i[0])+" has hit "+str(meleopponent[0])+" with their "+str(whip)+" and dealt "+str(hit)+" damage.")
											if meleopponent[1]<1:
												melewinner=i
											break
										if str(move.content).lower()=="!rocktail":
											if i[2]<1:
												rocktail = get(client.get_all_emojis(), name='rocktail')
												await client.send_message(message.channel, "You are out of "+str(rocktail)+". Please use `!dds` or `!whip`.")
												continue
											else:
												healing=random.randint(22,29)
												i[2]-=1
												i[1]+=healing
												if i[1]>99:
													i[1]=99
												await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
												rocktail = get(client.get_all_emojis(), name='rocktail')
												await client.send_message(message.channel, str(i[0])+" eats a "+str(rocktail)+" and heals "+str(healing)+" hp.")
												break

										elif str(move.content).lower()=="!dds":
											if i[3]<1:
												dds = get(client.get_all_emojis(), name='dds')
												await client.send_message(message.channel, "You are out of "+str(dds)+" specs. Please use `!rocktail` or `!whip`.")
												continue
											else:
												i[3]-=1
												hit=random.randint(0,20)+random.randint(0,20)
												meleopponent[1]-=hit
												if meleopponent[1]<0:
													meleopponent[1]=0
												await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
												dds = get(client.get_all_emojis(), name='dds')
												await client.send_message(message.channel, str(i[0])+" has used a "+str(dds)+" on "+str(meleopponent[0])+" and dealt "+str(hit)+" damage.")
												if meleopponent[1]<1:
													winner=i
												else:
													if random.randint(1,4)==4:
														meleopponent[4]=True
														meleopponent[6]=4
														await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
														dds = get(client.get_all_emojis(), name='dds')
														await client.send_message(message.channel, str(meleopponent[0])+" has been poisoned by the "+str(dds)+"!")
												break

										elif str(move.content).lower()=="!whip":
											hit=random.randint(0,27)
											meleopponent[1]-=hit
											await client.edit_message(melesent, embed=hpupdate(meleplayers, str(message.server.icon_url), "mele"))
											whip = get(client.get_all_emojis(), name='whip')
											await client.send_message(message.channel, str(i[0])+" has hit "+str(meleopponent[0])+" with their "+str(whip)+" and dealt "+str(hit)+" damage.")
											if meleopponent[1]<1:
												melewinner=i
											break
										else:
											await client.send_message(message.channel, "An **error** has occured. Make sure to use `!rocktail` `!dds` or `!whip`.")
											continue
						else:
							winnert=getvalue(int(winner[0].id), "tokens")
							c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(winnert+melebet+melebet, winner[0].id))
							conn.commit()
							await client.send_message(message.channel, "<@"+str(melewinner[0].id)+"> Has won the duel and gained "+'{:,}'.format(melebet*2)+" tokens!")
							meleduel=False
							melewinner=None
							break
				else:
					None
			else:
				None			
		#except:
	####################
	elif message.content.startswith("!magebox"):
		#try:
		if magicduel:
			await client.send_message(message.channel, "There is a magic duel already going on. Please wait until that one finishes.")
		else:
			enough=True
			magiccurrent=getvalue(int(message.author.id), "tokens")
			magicbet=formatok((message.content).split(" ")[1])

			if magicbet<100:
				await client.send_message(message.channel, "The minimum amount you can bet is **100** tokens.")
				enough=False

			if enough:
				magicduel=True
				c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(magiccurrent-magicbet, message.author.id))
				await client.send_message(message.channel, "<@"+str(message.author.id)+"> wants to duel for "+'{:,}'.format(magicbet)+" tokens. Use `!call` to accept the duel.")
				while True:
					call = await client.wait_for_message(timeout=60, channel=message.channel, content="!call")
					if call is None:
						await client.send_message(message.channel, "<@"+str(message.author.id)+">'s duel request has timed out.")
						c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(magiccurrent, message.author.id))
						magicduel=False
						break
					magiccaller=call.author
					if str(magiccaller.id)==str(message.author.id):
						await client.send_message(message.channel, "As exciting as it may sound, you cannot duel yourself ._.")
						continue
					magiccallertokens=getvalue(int(magiccaller.id), "tokens")
					if magiccallertokens<magicbet:
						await client.send_message(message.channel, "You don't have enough tokens to call that duel.")
						continue
					else:
						c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(magiccallertokens-magicbet, magiccaller.id))
						break

				if magicduel:
					#player=[member object, hp, sharks, frozen]
					magicgambler=[(message.author), 99, 5, False]
					magiccaller=[magiccaller, 99, 5, False]
					magicplayers=[magicgambler,magiccaller]
					magicwinner=None
					while True:
						if magicwinner==None:
							magicsent = await client.send_message(message.channel, embed=hpupdate(magicplayers, str(message.server.icon_url), "magic"))
							for i in magicplayers:
								if magicwinner!=None:
									break
								else:
									if i[3]==True:
										await client.send_message(message.channel, str(i[0])+" is frozen and cannot do anything this turn.")
										i[3]=False
										continue
									magicopponent=magicplayers[int(magicplayers.index(i))-1]
									await client.send_message(message.channel, str(i[0])+", it is your turn. Use `!rocktail`, `!blood` or `!ice`.")
									while True:
										move = await client.wait_for_message(timeout=20, channel=message.channel, author=i[0])
										if move is None:
											blood = get(client.get_all_emojis(), name='blood')
											await client.send_message(message.channel, "Took too long. Automatically used "+str(blood)+".")
											hit=random.randint(0,29)
											magicopponent[1]-=hit
											if magicopponent[1]<0:
												magicopponent[1]=0
											healed=int(hit*0.25)
											i[1]+=healed
											if i[1]>99:
												i[1]=99
											await client.edit_message(magicsent, embed=hpupdate(magicplayers, str(message.server.icon_url), "magic"))
											blood = get(client.get_all_emojis(), name='blood')
											await client.send_message(message.channel, str(i[0])+" has used "+str(blood)+" on "+str(magicopponent[0])+", dealt "+str(hit)+" damage, and was healed for "+str(healed)+" HP.")
											if magicopponent[1]<1:
												magicwinner=i
											break
										if str(move.content).lower()=="!rocktail":
											if i[2]<1:
												rocktail = get(client.get_all_emojis(), name='rocktail')
												await client.send_message(message.channel, "You are out of "+str(rocktail)+". Please use `!blood` or `!ice`.")
												continue
											else:
												healing=random.randint(22,29)
												i[2]-=1
												i[1]+=healing
												if i[1]>99:
													i[1]=99
												await client.edit_message(magicsent, embed=hpupdate(magicplayers, str(message.server.icon_url), "magic"))
												rocktail = get(client.get_all_emojis(), name='rocktail')
												await client.send_message(message.channel, str(i[0])+" eats a "+str(rocktail)+" and heals "+str(healing)+" hp.")
												break

										elif str(move.content).lower()=="!ice":
											hit=random.randint(0,30)
											magicopponent[1]-=hit
											if magicopponent[1]<0:
												magicopponent[1]=0
											await client.edit_message(magicsent, embed=hpupdate(magicplayers, str(message.server.icon_url), "magic"))
											ice = get(client.get_all_emojis(), name='ice')
											await client.send_message(message.channel, str(i[0])+" has used "+str(ice)+" on "+str(magicopponent[0])+" and dealt "+str(hit)+" damage.")
											if magicopponent[1]<1:
												magicwinner=i
											else:
												if random.randint(1,5)==5:
													magicopponent[3]=True
													ice = get(client.get_all_emojis(), name='ice')
													await client.send_message(message.channel, str(magicopponent[0])+" has been frozen from "+str(ice)+".")
											break

										elif str(move.content).lower()=="!blood":
											hit=random.randint(0,29)
											magicopponent[1]-=hit
											if magicopponent[1]<0:
												magicopponent[1]=0
											healed=int(hit*0.25)
											i[1]+=healed
											if i[1]>99:
												i[1]=99
											await client.edit_message(magicsent, embed=hpupdate(magicplayers, str(message.server.icon_url), "magic"))
											blood = get(client.get_all_emojis(), name='blood')
											await client.send_message(message.channel, str(i[0])+" has used "+str(blood)+" on "+str(magicopponent[0])+", dealt "+str(hit)+" damage, and was healed for "+str(healed)+" HP.")
											if magicopponent[1]<1:
												magicwinner=i
											break
										else:
											await client.send_message(message.channel, "An **error** has occured. Make sure to use `!rocktail` `!blood` or `!ice`.")
											continue
						else:
							winnert=getvalue(int(magicwinner[0].id), "tokens")
							c.execute("UPDATE rsmoney SET tokens={} WHERE id={}".format(winnert+magicbet+magicbet, magicwinner[0].id))
							conn.commit()
							await client.send_message(message.channel, "<@"+str(magicwinner[0].id)+"> Has won the duel and gained "+'{:,}'.format(magicbet*2)+" tokens!")
							magicduel=False
							magicwinner=None
							break
				else:
					None
			else:
				None			
		#except:

#website info
#total wallet
#donate system
#duel system
#more words

client.loop.create_task(my_background_task())
Bot_Token = os.environ['TOKEN']
client.run(str(Bot_Token))
#https://discordapp.com/oauth2/authorize?client_id=479862852895899649&scope=bot&permissions=0
 