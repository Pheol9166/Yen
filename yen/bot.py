import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json


load_dotenv()

class Yen(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents= discord.Intents.all()
        )
        
        with open("./config.json", "r", encoding="utf-8") as f:
            self.token: str = os.environ.get('BOT_TOKEN')
            self.id: int = int(os.environ.get('SERVER_ID'))
    
    def run(self):
        super().run(self.token)
        
    async def setup_hook(self):
            for file in os.listdir("./yen/Cogs"):
                if file.endswith(".py"):
                    await self.load_extension(f"yen.Cogs.{file.split('.')[0]}", )
            
            await self.tree.sync(guild= discord.Object(id=self.id))
            
    async def on_ready(self):
        print(f"{self.user} online 🟢")
        
    async def on_disconnect(self):
        print(f"{self.user} offline 🔴")