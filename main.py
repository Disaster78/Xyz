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

# Dictionary to keep track of messages already sent
messages_sent = {}

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

    # Check if the reaction is the target custom emoji
    for reaction in message.reactions:
        if reaction.emoji == custom_emoji and reaction.count >= TARGET_REACTION_COUNT:
            # Check if a message has already been sent for this message ID
            existing_message_id = messages_sent.get(payload.message_id)
            if existing_message_id is not None:
                try:
                    # Retrieve the existing message
                    existing_message = await channel.fetch_message(existing_message_id)
                except discord.NotFound:
                    logger.error("Existing message not found. Message likely deleted.")
                    return
                
                # Update the existing message
                embed = existing_message.embeds[0]  # Get the existing embed
                embed.set_footer(
                    text=f"Message sent at {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Check for attachments
                if message.attachments:
                    # Get the first attachment and set it as the image in the embed
                    attachment = message.attachments[0]
                    embed.set_image(url=attachment.url)
                
                # Edit the message
                await existing_message.edit(embed=embed)
                return
            
            # Wait for a short delay to allow for reaction count updates
            await asyncio.sleep(5)  # Adjust the delay time as needed
            
            # Check the reaction count again before sending the message
            message = await channel.fetch_message(payload.message_id)
            reaction = discord.utils.get(message.reactions, emoji=custom_emoji)
            if reaction and reaction.count >= TARGET_REACTION_COUNT:
                # Prepare the embed
                embed = discord.Embed(
                    description=message.content,
                    color=discord.Color.from_rgb(255, 255, 255)  # White color
                )
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar.url
                )
                embed.set_footer(
                    text=f"{custom_emoji} {reaction.count} in #{channel.name} | Message sent at {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Check for attachments
                if message.attachments:
                    # Get the first attachment and set it as the image in the embed
                    attachment = message.attachments[0]
                    embed.set_image(url=attachment.url)
                
                # Send the message with the emoji and reaction count along with the embed
                target_channel = bot.get_channel(CHANNEL2_ID)
                reaction_info = f"**{reaction.emoji} {reaction.count}** in #{channel.name}"
                content = f"{reaction_info}\n{message.jump_url}"
                sent_message = await target_channel.send(content=content, embed=embed)
                
                # Mark the message ID as sent
                messages_sent[payload.message_id] = sent_message.id

# Keep the bot running with keep_alive
keep_alive()

# Run the bot
bot.run(TOKEN)
                              
