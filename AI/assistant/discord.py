import discord

# Create an instance of a client with proper intents to read DMs
intents = discord.Intents.default()
intents.dm_messages = True  # Enable DM message-related events

client = discord.Client(intents=intents)

# Called when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Called when a new message is received
@client.event
async def on_message(message):
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel):
        print(f'DM from {message.author}: {message.content}')
    else:
        # Handle regular server messages (if needed)
        print(f'Message from {message.author} in {message.channel.name}: {message.content}')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
client.run('YOUR_BOT_TOKEN')
