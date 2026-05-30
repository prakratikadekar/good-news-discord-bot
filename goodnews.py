import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks 
import os
import random
import feedparser
import time
from html.parser import HTMLParser
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

good_news_links = ["https://www.sciencedaily.com/rss/top/science.xml", "https://www.dailygood.org/feed/", "https://www.positive.news/feed/", "https://www.onlygoodnewsdaily.com/feed/", "https://www.onlygoodnewsdaily.com/blog-feed.xml", "https://www.onlygoodnewsdaily.com/blog-feed.xml"]

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')
        get_good_news.start()


intents = discord.Intents.default()
client = Client(intents=intents)

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        
    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)

def connect_data_without_tags(content):
    stripped_data = HTMLStripper()
    stripped_data.feed(content)
    return stripped_data.get_text()
        

@tasks.loop(hours=24)
async def get_good_news():
    
    link_for_today = random.choice(good_news_links)

    feed = feedparser.parse(link_for_today)

    if feed.entries:
        news_entry = random.choice(feed.entries)
        await post_good_news(news_entry)

    else:
        get_good_news.start()


async def post_good_news(news_entry):
    channel = client.get_channel(CHANNEL_ID)

    embed = discord.Embed(title=news_entry.title, url=news_entry.link, description=connect_data_without_tags(news_entry.summary), color=discord.Color.dark_green())
    embed.set_thumbnail(url="https://stardewvalleywiki.com/mediawiki/images/c/c8/Emojis043.png")
    
    await channel.send(embed=embed)
    print("News has been posted in channel")
    

client.run(TOKEN)
    