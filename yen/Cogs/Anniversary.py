from typing import Optional
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice
from yen.type import DateJSON, DateType
import datetime
from pytz import timezone
import json


#TODO: 검색 기능 추가, N주년 기념 메소드 제작
class Anniversary(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminder.start()
        self.day_checker.start()
        self.timezone = timezone('Asia/Seoul')
        
    @staticmethod
    def load_dates() -> DateJSON | dict:
        try:
            with open("./yen/DB/dates.json", 'r', encoding="utf-8") as fr:
                dates: DateJSON = json.load(fr)
            return dates
        except:
            dates: dict = {}
            return dates
        
    @staticmethod
    def write_dates(dates: DateJSON):
        with open("./yen/DB/dates.json", 'w', encoding="utf-8") as fw:
            json.dump(dates, fw, ensure_ascii=False, indent=4)
    
    @staticmethod
    def search_date_by_name(id: str, dates: DateJSON, name: str) -> DateType:
        try:
            for date in dates[id]:
                if name == date['name']:
                    return date
        except:
            raise Exception
        
    @staticmethod
    def check_duplicate_id(id: str) -> bool:
        dates: DateJSON = Anniversary.load_dates()
        if id in dates.keys():
            return True
        else:
            return False
        
    @staticmethod
    def check_duplicate_date(id: str, date: DateType) -> bool:
        dates = Anniversary.load_dates()
        if date in dates[id]:
            return True
        else:
            return False
        
    @staticmethod
    def check_date_name(name: str) -> bool:
        if name == "처음 사귄 날":
            return False
        else:
            return True
    
    @staticmethod
    def check_date_format(date: str) -> bool:
        try:
            if datetime.datetime.strptime(date, "%Y-%m-%d"):
                return True
        except:
            return False
    
    async def autocomplete_date_name_param(self, interaction: discord.Interaction, value: str) -> list[Choice[str]]:
        user_id = str(interaction.user.id)
        dates: list[DateType] = Anniversary.load_dates()[user_id]    
        return [Choice(name=date['name'], value=date['name']) for date in dates if value in date['name']]        
    
    @app_commands.command(name="설정하기", description="기념일을 처음 설정해요!")
    async def set_anniversary(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if Anniversary.check_duplicate_id(user_id):
            await interaction.response.send_message("이미 기념일을 설정하셨어요!")
        else:
            def check(message: discord.Message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            await interaction.followup.send("처음 사귄 날을 입력해주세요! (예시: 2023-3-21)")
            date_message = await self.bot.wait_for('message', check=check)
            date: str = date_message.content
            
            if Anniversary.check_date_format(date):
                data: DateJSON | dict = Anniversary.load_dates()
                data[user_id]: list[DateType] = [{'name': "처음 사귄 날", 'date': date}]
                Anniversary.write_dates(data)
                                
                embed = discord.Embed(title="기념일을 설정했어요!", color=0xFFFFFF)
                embed.add_field(name="🔑 기념일", value="처음 사귄 날", inline=False)
                embed.add_field(name="📆 날짜", value=date, inline=False)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("기념일 형식은 YYYY-MM-DD여야 해요... 다시 시도해주세요!")
                
    @app_commands.command(name="확인하기", description="기념일을 확인해요!")
    async def get_anniversary(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if Anniversary.check_duplicate_id(user_id):
            dates: DateJSON = Anniversary.load_dates()
            embed = discord.Embed(title=f"{interaction.user.name}님의 기념일 리스트", color=0xFFFFFF)
            for date in dates[user_id]:
                embed.add_field(name="🔑 기념일", value=date['name'], inline=False)
                embed.add_field(name="📆 날짜", value=date['date'], inline=False)   
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("기념일을 설정하지 않았어요... 설정하기 명령어를 통해 가능해요!")
    
    @app_commands.command(name="날짜추가", description="기념일을 추가해요!(설정이 되어있어야 해요!)")
    @app_commands.describe(date_name="추가할 기념일 이름", date="추가할 기념일의 날짜(YYYY-MM-DD로 입력해주세요!)")
    async def add_anniversary(self, interaction: discord.Interaction, date_name: str, date: str):
        user_id = str(interaction.user.id)
        if Anniversary.check_duplicate_id(user_id):
            dates: DateJSON = Anniversary.load_dates()
            new_date: DateType = {'name': date_name, 'date': date}
            
            if Anniversary.check_duplicate_date(user_id, new_date):
                await interaction.response.send_message("기념일이 이미 등록되어 있어요!")
            else:
                if Anniversary.check_date_format(date):
                    dates[user_id].append(new_date)
                    Anniversary.write_dates(dates)

                    embed = discord.Embed(title="기념일을 추가했어요!", color=0xFFFFFF)
                    embed.add_field(name="🔑 추가된 기념일", value=date_name, inline=False)
                    embed.add_field(name="📆 날짜", value=date, inline=False) 
                
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("기념일 형식은 YYYY-MM-DD여야 해요... 다시 시도해주세요!")
        else:
            await interaction.response.send_message("기념일을 설정하지 않았어요... 설정하기 명령어를 통해 가능해요!")
            
    @app_commands.command(name="날짜제거", description="기념일을 제거해요!(설정이 되어있어야 해요!)")
    @app_commands.describe(date_name="제거할 기념일 이름")
    async def delete_anniversary(self, interaction: discord.Interaction, date_name: str):
        user_id = str(interaction.user.id)
        if Anniversary.check_duplicate_id(user_id):
            dates = Anniversary.load_dates()
            date = Anniversary.search_date_by_name(user_id, dates, date_name)
            dates[user_id].remove(date)
            Anniversary.write_dates(dates)
            embed = discord.Embed(title="기념일을 제거했어요!", color=0xFFFFFF)
            embed.add_field(name="🔑 제거된 기념일", value=date['name'], inline=False)
            embed.add_field(name="📆 날짜", value=date['date'], inline=False)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("기념일을 설정하지 않았어요... 설정하기 명령어를 통해 가능해요!")             
    @delete_anniversary.autocomplete("date_name")
    async def autocomplete_date_name_param(self, interaction: discord.Interaction, value: str) -> list[Choice[str]]:
        user_id = str(interaction.user.id)
        dates: list[DateType] = Anniversary.load_dates()[user_id]    
        return [Choice(name=date['name'], value=date['name']) for date in dates[1:] if value in date['name']]
        
    @app_commands.command(name="날짜수정", description="기념일을 수정해요!(설정이 되어있어야해요!)")
    @app_commands.describe(date_name="찾을 기념일 이름", new_name="새로운 이름", new_date="새로운 날짜")
    @app_commands.autocomplete(date_name=autocomplete_date_name_param)
    async def edit_anniversary(self, interaction: discord.Interaction, date_name: str, new_name: Optional[str]=None, new_date: Optional[str]=None):
        user_id = str(interaction.user.id)
        if Anniversary.check_duplicate_id(user_id):
            dates: DateJSON = Anniversary.load_dates()
            date: DateType = Anniversary.search_date_by_name(user_id, dates, date_name)
            embed = discord.Embed(title="기념일을 수정했어요!", color=0xffffff)

            if new_name:
                if Anniversary.check_date_name(date_name):
                    embed.add_field(name="🔑 수정된 기념일", value=f"{date['name']} -> {new_name}", inline=False)
                    date['name'] = new_name
                else:
                    await interaction.response.send_message("처음 사귄 날 기념일은 이름을 수정할 수 없어요... 다시 시도해주세요!")
                    return
            
            if new_date:
                if Anniversary.check_date_format(new_date):
                    embed.add_field(name="📆 수정된 날짜", value=f"{date['date']} -> {new_date}", inline=False)
                    date['date'] = new_date
                else:
                    await interaction.response.send_message("날짜 형식이 맞지 않아요... 다시 시도해주세요!")
                    return

            if new_name or new_date:
                if Anniversary.check_duplicate_date(user_id, date):
                    await interaction.response.send_message("기념일이 중복되었어요! 다시 시도해주세요...")
                else:
                    Anniversary.write_dates(dates)
                    await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("이름이나 날짜 둘 중 하나를 입력해주세요!")
        else:
            await interaction.response.send_message("기념일을 설정하지 않았어요... 설정하기 명령어를 통해 가능해요!")

    @tasks.loop(minutes=1.0)
    async def reminder(self):
        now: datetime.datetime = datetime.datetime.now()
        now = now.astimezone(self.timezone)
        if now.hour == 8 and now.minute == 0:
            dates: DateJSON = Anniversary.load_dates()
            for user_id in dates.keys():
                user: discord.User = self.bot.get_user(int(user_id))
                if user:
                    for date in dates[user_id]:
                        anniversary: datetime.datetime = datetime.datetime.strptime(date["date"], "%Y-%m-%d")
                        anniversary = anniversary.astimezone(self.timezone)
                        if anniversary.month == now.month and anniversary.day == now.day:                
                            embed = discord.Embed(title=f"오늘은 기념일이에요! 🎉", color=0xFFFFFF)
                            embed.add_field(name="🔑 기념일", value=date['name'], inline=False)
                            embed.add_field(name="📆 날짜", value=date['date'], inline=False)
            
                            await user.send(f"{user.mention}님, 오늘은 {date['name']}이에요! ✨", embed=embed)
        
    @tasks.loop(minutes=1.0)
    async def day_checker(self):
        now: datetime.datetime = datetime.datetime.now()
        now = now.astimezone(self.timezone)
        if now.hour == 8 and now.minute == 0:
            dates: DateJSON = Anniversary.load_dates()
            for user_id in dates:
                user: discord.User = self.bot.get_user(int(user_id))
                if user:
                    first_day: DateType = Anniversary.search_date_by_name(user_id, dates, "처음 사귄 날")
                    first_day_date: datetime.datetime = datetime.datetime.strptime(first_day['date'], "%Y-%m-%d")
                    first_day_date = first_day_date.astimezone(self.timezone)
                    day_count: int = (now.date() - first_day_date.date()).days
                    
                    await user.send(f"{user.mention}님! 오늘은 {first_day['name']}로부터 {day_count + 1}일째에요!❤")
    
    @reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()
    
    @day_checker.before_loop
    async def before_day_checker(self):
        await self.bot.wait_until_ready()
            
async def setup(bot: commands.Bot):
    await bot.add_cog(
        Anniversary(bot),
        guilds= [discord.Object(id=bot.id)]
    )       