from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from yen.type import QuoteJSON, QuoteType
import random
import json


class Quotes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @staticmethod
    def load_quotes() -> list[QuoteType]:
        with open("./yen/DB/quotes.json", 'r', encoding="utf-8") as fr:
            data: QuoteJSON = json.load(fr)
        return data['quotes']
    
    @staticmethod
    def write_quotes(data: list[QuoteType]) -> None:
        with open("./yen/DB/quotes.json", 'w', encoding="utf-8") as fw:
            quote_json = {"quotes": data}
            json.dump(quote_json, fw, ensure_ascii=False, indent=4)
                
    @staticmethod
    def search_quote(data: list[QuoteType], quote: str) -> QuoteType:
        for quote_one in data:
            if quote_one['quote'] == quote:
                return quote_one
        raise Exception
                
    @staticmethod
    async def check_admin(interaction: discord.Interaction) -> Optional[bool]:
        if interaction.guild:
            member: discord.Member = interaction.guild.get_member(interaction.user.id)
            if member.guild_permissions.administrator:
                return True
            else:
                await interaction.response.send_message("관리자가 아니에요!")
        else:
            await interaction.response.send_message("이 명령은 서버에서만 실행될 수 있어요!")
    
    async def autocomplete_quote_param(self, interaction: discord.Interaction, value: str) -> list[Choice[str]]:
        quotes: list[QuoteType] = Quotes.load_quotes()
        return [Choice(name=quote['quote'], value=quote['quote']) for quote in quotes if value in quote['quote']]
       
    @app_commands.command(name="추천받기", description="예니가 사랑에 관한 문구를 추천해줘요!")
    async def recommend(self, interaction: discord.Interaction):
        quotes: list[QuoteType] = Quotes.load_quotes()
        quote: QuoteType = random.choice(quotes)
        embed = discord.Embed(title="🖋 예니의 문구 추천!", color=0xffffff)
        embed.add_field(name="", value=f"***{quote['quote']}***", inline=False)
        embed.set_footer(text=f"-{quote['person']}-")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="문구추가", description="예니가 추천하는 문구를 추가해요!(관리자용)")
    @app_commands.describe(quote="추가할 문구", author="말한 사람")
    @app_commands.autocomplete(quote=autocomplete_quote_param)
    async def add_quote(self, interaction: discord.Interaction, quote: str, author: str):
        if Quotes.check_admin(interaction):
            quotes: list[QuoteType] = Quotes.load_quotes()
            contents: list[str] = list(map(lambda x: x['quote'], quotes))
            if quote in contents:
                raise Exception
            else:
                quotes.append({
                    "quote": quote,
                    "person": author
                })
                Quotes.write_quotes(quotes)
            
                embed = discord.Embed(title="문구가 추가되었어요!", color=0xffffff)
                embed.add_field(name="📔 추가된 문구", value=f"***{quote}***", inline=False)
                embed.add_field(name="🖋 말한 사람", value=author, inline=False)
            
                await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="문구제거", description="예니가 추천하는 문구를 제거해요!(관리자용)")
    @app_commands.describe(quote="제거할 문구")
    @app_commands.autocomplete(quote=autocomplete_quote_param)
    async def delete_quote(self, interaction: discord.Interaction, quote: str):
        if Quotes.check_admin(interaction):
            quotes: list[QuoteType] = Quotes.load_quotes()
            quote_one = Quotes.search_quote(quotes, quote)
            author: str = quote_one['person']
            quotes.remove(quote_one)
            Quotes.write_quotes(quotes)
            
            embed = discord.Embed(title="문구가 제거되었어요!", color=0xffffff)
            embed.add_field(name="📔 제거된 문구", value=f"***{quote}***", inline=False)
            embed.add_field(name="🖋 말한 사람", value=author, inline=False)
            
            await interaction.response.send_message(embed=embed)                                
                    
    @app_commands.command(name="문구수정", description="예니가 추천하는 문구를 수정해요!(관리자용)")
    @app_commands.describe(quote="수정할 문구", new_quote="새로운 문구", new_author="새로운 사람")
    @app_commands.autocomplete(quote=autocomplete_quote_param)
    async def edit_quote(self, interaction: discord.Interaction, quote: str, new_quote: Optional[str]=None, new_author: Optional[str]=None):
        if Quotes.check_admin(interaction):
            quotes: list[QuoteType] = Quotes.load_quotes()
            quote_one: QuoteType = Quotes.search_quote(quotes, quote)
            embed = discord.Embed(title="문구가 수정되었어요!", color=0xffffff)
            
            if new_quote:
                embed.add_field(name="📜 수정 전 문구", value=quote, inline=False)
                embed.add_field(name="📔 수정 후 문구", value=f"***{new_quote}***", inline=False)
                quote_one['quote'] = new_quote
                              
            if new_author:
                embed.add_field(name="✏ 수정 전 사람", value=quote_one['person'], inline=False)
                embed.add_field(name="🖋 수정 후 사람", value=new_author, inline=False)
                quote_one['person'] = new_author
            
            if new_quote or new_author:
                Quotes.write_quotes(quotes)
                await interaction.response.send_message(embed=embed)
            else:
                raise Exception
            
async def setup(bot: commands.Bot):
    await bot.add_cog(
        Quotes(bot),
        guilds= [discord.Object(id=bot.id)]
    )                