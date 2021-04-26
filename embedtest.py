import discord, json, requests
from ratelimit import limits

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if 'happy birthday' in message.content.lower():
        banemoji = client.get_emoji(ID_GOES_HERE)
        await message.add_reaction('<:ban:825136806285672498>')

client.run('ODM0NDA4ODA1MDYzNTg5OTQ5.YIAdwQ.qkhU0BtHtvLmtnjaPjM1mJ8IX8E')

elif payload.emoji.name == ':x:':
        embedcontents=msg.embed.fields
        link=(embed.fields[1].value).split('/')
        msg_id = int(link[5])
        message = await channel.fetch_message(msg_id)
        await message.delete()
        await msg.embed.clear_fields()
        toxembed=discord.Embed(title='Deleted by {payload.member}',colour = discord.Colour.red())
        await msg.edit(embed=toxembed)
    elif payload.emoji.name == ':leg:':
        embedcontents=msg.embed.fields
        userid=int(embed.fields[2].value)
        await client.guild.kick(user=userid, reason="AI")
        await msg.embed.clear_fields()
        toxembed=discord.Embed(title='Kicked by {payload.member}',colour = discord.Colour.red())
        await msg.edit(embed=toxembed)
    elif payload.emoji.name == ':BAN:':
        embedcontents=msg.embed.fields
        userid=int(embed.fields[2].value)
        await client.guild.ban(user=userid, reason="AI")
        await msg.embed.clear_fields()
        toxembed=discord.Embed(title='Banned by {payload.member}',colour = discord.Colour.red())
        await msg.edit(embed=toxembed)