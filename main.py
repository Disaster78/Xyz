import os
import discord
import logging
from discord.ext import commands
from keep_alive import keep_alive  # Import the keep_alive function
from datetime import datetime
import asyncio  # Import asyncio for delaying message sending

# Access token from environment variable
TOKEN = os.environ['TOKEN']

# Target channel ID where embeds are sent
CHANNEL2_ID = 1203597259774885908  # Channel where embeds are sent

# Custom emoji details and the required number of reactions
CUSTOM_EMOJI_NAME = 'upvote'  # The name of the custom emoji
CUSTOM_EMOJI_ID = 1203698304001777714  # The ID of the custom emoji
TARGET_REACTION_COUNT = 4  # Number of reactions required

# Unique marker reaction to indicate a message has been processed
MARKER_EMOJI = '✅'  # You can use any emoji as a marker

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
        logger.error("Custom emoji not found")
        return

    # Check if the marker reaction is already present
    for reaction in message.reactions:
        if str(reaction.emoji) == MARKER_EMOJI:
            return

    # Check if the reaction is the target custom emoji
    for reaction in message.reactions:
        if reaction.emoji == custom_emoji and reaction.count >= TARGET_REACTION_COUNT:
            # Check if a message has already been sent for this message I

            # Wait for a short delay before sending the message
            await asyncio.sleep(7)  # Adjust the delay time as needed

            # Check the reaction count again before sending the message
            message = await channel.fetch_message(payload.message_id)
            reaction = discord.utils.get(message.reactions, emoji=custom_emoji)
            if reaction and reaction.count >= TARGET_REACTION_COUNT:
                # Prepare the embed
                embed = discord.Embed(
                    description=message.content,
                    color=discord.Color.from_rgb(0, 255, 0)  # lime color
                )
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar.url
                )
                timestamp = message.created_at.strftime('%m/%d/%Y %I:%M %p')
                embed.set_footer(
                    text=f"{timestamp} | In #{channel.name}"
                )
                
                # Check for attachments
                if message.attachments:
                    # Get the first attachment and set it as the image in the embed
                    attachment = message.attachments[0]
                    embed.set_image(url=attachment.url)
                
                # Send the message with the reaction count along with the embed
                target_channel = bot.get_channel(CHANNEL2_ID)
                reaction_info = f"**{custom_emoji} {reaction.count} [Jump To Message]({message.jump_url}**)"
                sent_message = await target_channel.send(content=reaction_info, embed=embed)
                
                # Add the marker reaction to indicate the message has been processed
                await message.add_reaction(MARKER_EMOJI)

# Keep the bot running with keep_alive
keep_alive()

# Run the bot
bot.run(TOKEN)
    
