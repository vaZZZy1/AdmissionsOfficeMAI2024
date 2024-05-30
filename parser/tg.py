import asyncio

from baseclass import BaseParser,RequestToML,TextEntry
from typing import List
from telethon import TelegramClient, events


class TgParser(BaseParser):

    def __init__(self,api_id:int,api_hash:str):
        self.client = TelegramClient('app', api_id,api_hash, system_version="4.16.30-vxXYU")
    def parse(self, raw_data:List[str]) -> RequestToML:
        d = dict()
        for i in range(len(raw_data)):
            d[str(i+1)] = TextEntry(raw_data)
        res = RequestToML(d)
        return res

    async def handleEvent(self,event):
        print(event.raw_text)
        print(self.parse([event.raw_text]))    #no idea how to  save  to db

    def start(self,channelIDs:List[str]):
        self.client.add_event_handler(self.handleEvent,events.NewMessage(chats = channelIDs))
        self.client.start()
        self.client.run_until_disconnected()

# tg = TgParser( 20043925, "23e4754bd44687a84589ba0489a700fa")
# tg.start( [<num_channel_id1>,<num_channel_id2>,<num_channel_id3>])
