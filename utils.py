import os
import requests
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

iptv_link = "https://gist.githubusercontent.com/pahadi/a048909a292d345d45g4g5ff/raw/34f9288582d480d9eea490d09d9f8t96ne0d/links.json"

def fetch_data(url):
    data = requests.get(url)
    data = data.text
    return json.loads(data)

def getChannels(app, message):
    data = fetch_data(iptv_link)
    channelsList = ""
    for i in data:
        channelsList += f"{i}\n"
    message.reply_text(text=f"Available Channels:\n\n{channelsList}")
