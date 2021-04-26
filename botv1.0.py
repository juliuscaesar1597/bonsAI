import discord, json, requests
from ratelimit import limits
import string
from settings import API_KEY, DISCORD_TOKEN

#set up Discord client
client = discord.Client()

#rate limit decorator because Perspective API limits you to 1 query per second 
@limits(calls=1, period=1)
def toxic_check(message):
    api_key = API_KEY
    url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' + '?key=' + api_key)
    
#Ask Perspective to analyize for "attacks on identity." Other values such as TOXICITY can be found in their docs
    data_dict = {
        'comment': {'text': message},
        'languages': ['en'],
        'requestedAttributes': {'THREAT': {}, 'SEVERE_TOXICITY':{}, 'IDENTITY_ATTACK':{}},
        'doNotStore': 'true'
    }

    response = requests.post(url=url, data=json.dumps(data_dict)) 
    response_dict = json.loads(response.content)
    global thrattack
    global toxattack
    global toxattack
    global attack 
    thrattack = response_dict["attributeScores"]["THREAT"]["summaryScore"]["value"]
    toxattack = response_dict["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
    ideattack = response_dict["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"]
    attack= max(thrattack,toxattack,ideattack)
    return attack


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='with AI'))
    

@client.event
async def on_message(message): 
    if message.author == client.user:
        return
    try:
        if toxic_check(message.clean_content) > 0.9:
            toxreason= await get_tox()
            jump_url = f"[Click to see context.]({message.jump_url})"
            mess=message.content
            chanl= client.get_channel(834778270968446976)
            toxembed=discord.Embed(title='New potentially inappropriate message:',colour = discord.Colour.red())
            name= f"{message.author.name}#{message.author.discriminator}"
            toxembed.set_author(name=name , icon_url=message.author.avatar_url)
            toxembed.description = mess
            toxembed.add_field(name = "Flagged for: ", value =toxreason)
            toxembed.add_field(name = "Context:", value =jump_url)
            toxembed.add_field(name = "User ID:", value =message.author.id)
            sendembed = await chanl.send(embed=toxembed)
            banemoji = '<:BAN:835119271846871060>'
            await sendembed.add_reaction("✅")
            await sendembed.add_reaction("❌")
            await sendembed.add_reaction("🦵")
            await sendembed.add_reaction(banemoji)
    except:
        pass
async def get_tox():
    global typeattack
    if thrattack == attack:
        typeattack="Threat"
    elif toxattack == attack:
        typeattack="Severe Toxicity"
    else:
        typeattack="Identity Attack"
    return typeattack
@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id != 834778270968446976: 
        return 
    if payload.user_id == client.user.id: 
        return

    channel = client.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    guild=631730211880435752
    embed = msg.embeds[0]
    discorduser=await client.fetch_user(payload.user_id)

    if payload.emoji.name == '✅':
        embedcontents=embed.fields
        link=(embed.fields[1].value) 
        embed = discord.Embed(
			title=f"Approved by {discorduser}",
		    colour=discord.Color.green(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    elif payload.emoji.name == '❌':
        embedcontents=embed.fields
        link=(embed.fields[1].value)
        linksplit=(embed.fields[1].value).split('/')
        orimsg_id = int(re.sub(r'[)]', '', linksplit[6]))
        orichannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await orichannel.fetch_message(orimsg_id)
        await originalmessage.delete()
        embed = discord.Embed(
			title=f"Deleted by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    elif payload.emoji.name == '🦵':
        embedcontents=embed.fields
        link=(embed.fields[1].value)
        linksplit=(embed.fields[1].value).split('/')
        orimsg_id = int(re.sub(r'[)]', '', linksplit[6]))
        orichannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await orichannel.fetch_message(orimsg_id)
        oriuser= await client.fetch_user(int(embed.fields[2].value))
        await originalmessage.delete()
        kickguild = await client.fetch_guild(guild)
        await kickguild.kick(user=oriuser, reason=(embedcontents[0].value))
        embed = discord.Embed(
			title=f"Kicked by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    elif payload.emoji.name == 'BAN':
        embedcontents=embed.fields
        link=(embed.fields[1].value)
        linksplit=(embed.fields[1].value).split('/')
        orimsg_id = int(re.sub(r'[)]', '', linksplit[6]))
        orichannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await orichannel.fetch_message(orimsg_id)
        oriuser= await client.fetch_user(int(embed.fields[2].value))
        await originalmessage.delete()
        kickguild = await client.fetch_guild(guild)
        await kickguild.ban(user=oriuser, reason=(embedcontents[0].value))
        embed = discord.Embed(
			title=f"Banned by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    else:
        pass

client.run(DISCORD_TOKEN)