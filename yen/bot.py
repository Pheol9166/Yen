import discord
from discord.ext import commands
import os
import json


class Yen(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents= discord.Intents.all()
        )
        
        with open("./config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            self.token = config['Yen']['token']
            self.id = config['Yen']['id']
    
    def run(self):
        super().run(self.token)
        
    async def setup_hook(self):
            for file in os.listdir("./yen/Cogs"):
                if file.endswith(".py"):
                    await self.load_extension(f"yen.Cogs.{file.split('.')[0]}", )
            
            await self.tree.sync(guild= discord.Object(id=self.id))
            
    async def on_ready(self):
        print(f"{self.user}가 디스코드에 연결되었어요!")
        
    async def on_disconnect(self):
        print(f"{self.user} offline 🔴")