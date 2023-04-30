import discord
from discord.ext import commands
from discord import app_commands
from yen.type import JSON
from dotenv import load_dotenv
import os
import requests
import random


load_dotenv()

class Map(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.url: str = "https://dapi.kakao.com/v2/local/search/keyword.json"
        self.headers: JSON = {"Authorization": f"KakaoAK {os.environ.get('KAKAO_API_KEY')}"}
    
    def search_map(self, category: str, loc: str, name: str, num: int) -> discord.Embed:
        params: JSON = {"query": f"{loc} {name}", "category_group_code": category, "radius": 1000}
        response: requests.Response = requests.get(self.url, headers=self.headers, params=params)
        data: JSON = response.json()
        
        if data.get("documents"):
            results: list[JSON] = data["documents"]
            if num > len(results):
                places: list[JSON] = random.sample(results, len(results))
            else:
                places: list[JSON] = random.sample(results, num)
                
            embed = discord.Embed(title="🔎 검색 결과", description="예니가 추천 장소를 알려줘요!", color=0xffffff)
            for place in places:
                place_name: str = place["place_name"]
                place_address: str = place["address_name"]
                place_url: str = place["place_url"]
            
                embed.add_field(name="💡 장소명", value=place_name)
                embed.add_field(name="🔖 주소", value=place_address)
                embed.add_field(name="📌 URL", value=place_url, inline=False)
            
            return embed
                    
    @app_commands.command(name="맛집추천", description="주변 맛집을 추천해줘요!")
    @app_commands.describe(loc="검색할 위치", food="음식 종류나 이름", n="찾을 장소 수(default: 1)")
    async def search_restaurant(self, interaction: discord.Interaction, loc: str, food: str="", n: int=1):
        embed: discord.Embed = self.search_map("FD6", loc, food, n)
        if embed:    
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("검색 결과가 없어요...")
    
    @app_commands.command(name="카페추천", description="주변 카페를 추천해줘요!")
    @app_commands.describe(loc="검색할 위치", name="카페 종류나 이름", n="찾을 장소 수(default: 1)")
    async def search_cafe(self, interaction: discord.Interaction, loc: str, name: str="", n: int=1):        
        embed: discord.Embed = self.search_map("CE7", loc, name, n)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("검색 결과가 없어요...")
    
    @app_commands.command(name="데이트추천", description="주변 놀 곳을 추천해요!")
    @app_commands.describe(loc="검색할 위치", name="놀 곳의 종류나 이름", n="찾을 장소 수(default: 1)")    
    async def search_play(self, interaction: discord.Interaction, loc: str, name: str="", n: int=1):
        embed: discord.Embed = self.search_map("CT1", loc, name, n)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("검색 결과가 없어요...")
    
    @app_commands.command(name="산책추천", description="주변 걸을 곳을 추천해요!")
    @app_commands.describe(loc="검색할 위치", name="걸을 곳의 종류나 이름", n="찾을 장소 수(default: 1)")    
    async def search_walk(self, interaction: discord.Interaction, loc: str, name: str="공원", n: int=1):
        embed: discord.Embed = self.search_map("", loc, name, n)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("검색 결과가 없어요...")    
    
    @app_commands.command(name="장소검색", description="찾는 장소를 검색해요!")
    @app_commands.describe(loc="검색 장소", n= "찾을 장소 수(default: 1)")
    async def search_place(self, interaction: discord.Interaction, loc: str, n: int=1):
        embed: discord.Embed = self.search_map("", loc, "", n)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("검색 결과가 없어요...")              
            
async def setup(bot: commands.Bot):
    await bot.add_cog(
        Map(bot),
        guilds= [discord.Object(id=bot.id)]
    )                