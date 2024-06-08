import discord
from discord.ext import commands

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = os.environ['TOKEN']

# Target channel ID where embeds are sent
CHANNEL2_ID = 1203597259774885908  # Channel where embeds are sent

# Custom emoji details and the required number of reactions
CUSTOM_EMOJI_NAME = 'upvote'  # The name of the custom emoji
CUSTOM_EMOJI_ID = 1203698304001777714  # The ID of the custom emoji
TARGET_REACTION_COUNT = 1  # Number of reactions required

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='.', intents=intents)

def get_custom_emoji(bot, emoji_name, emoji_id):
    return discord.utils.get(bot.emojis, name=emoji_name, id=emoji_id)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_raw_reaction_add(payload):
    # Retrieve the channel and message
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    # Retrieve the custom emoji
    custom_emoji = get_custom_emoji(bot, CUSTOM_EMOJI_NAME, CUSTOM_EMOJI_ID)
    if custom_emoji is None:
        print("Custom emoji not found")
        return

    # Check if the reaction is the target custom emoji
    for reaction in message.reactions:
        if reaction.emoji == custom_emoji and reaction.count >= TARGET_REACTION_COUNT:
            # Prepare the embed
            embed = discord.Embed(
                description=f"[Jump to message]({message.jump_url})",
                color=discord.Color.white()
            )
            embed.add_field(name="Message Content", value=message.content, inline=False)
            
            # Send the embed and the normal message to the target channel
            target_channel = bot.get_channel(CHANNEL2_ID)
            await target_channel.send(embed=embed)
            await target_channel.send(f"{custom_emoji} {reaction.count}")
            break

bot.run(TOKEN)
