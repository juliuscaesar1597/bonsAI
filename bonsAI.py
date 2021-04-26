import discord, json, requests
from ratelimit import limits


#set up Discord client
client = discord.Client()

#rate limit decorator because Perspective API limits you to 1 query per second
@limits(calls=1, period=1)
def toxic_check(message):
    api_key = 'AIzaSyDgnzWz2GdFUxlbypi9M0jkAJQWmoPABYg'
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
    thrattack = response_dict["attributeScores"]["THREAT"]["summaryScore"]["value"]
    toxattack = response_dict["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
    ideattack = response_dict["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"]
    attack= max(thrattack,toxattack,ideattack)
    return attack

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    try:
        if toxic_check(message.clean_content) > 0.9: 
            jump_url = f"[Click to see context]({message.jump_url})"
            mess=message.content
            chanl= client.get_channel(834778270968446976)
            e=discord.Embed(title='New potentially inappropriate message:',colour = discord.Colour.red())
            name= f"{message.author.name}#{message.author.discriminator}"
            e.set_author(name=name , icon_url=message.author.avatar_url)
            e.description = mess
            e.add_field(name = "Context:", value =jump_url)
            await chanl.send(embed=e)
    except:
        pass

client.run('ODM0NDA4ODA1MDYzNTg5OTQ5.YIAdwQ.qkhU0BtHtvLmtnjaPjM1mJ8IX8E')