import discord
import json
import datetime
import asyncio

class DateBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load the settings from the settings.json file
        with open('settings.json', 'r') as f:
            self.settings = json.load(f)

    async def on_ready(self):
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        # Schedule the daily message to be sent at 8am
        await self.send_date_count_task()

    async def set_anniversary(self, ctx):
        """Set your anniversary date"""
        await ctx.send("Please enter your anniversary date in the following format: dd/mm/yyyy")
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()
        try:
            response = await self.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You didn't enter a valid date in time. Please try again.")
            return
        date = datetime.datetime.strptime(response.content, '%d/%m/%Y').date()
        user_id = str(ctx.author.id)
        if user_id not in self.settings:
            self.settings[user_id] = {}
        self.settings[user_id]['anniversary'] = date.strftime('%d/%m/%Y')
        # Save the updated settings to the settings.json file
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
        await ctx.send(f"Your anniversary date has been set to {date.strftime('%d %B %Y')}")
        
    async def send_date_count_task(self):
        """Send a message to the server every day at 8am with the number of days since the user's anniversary"""
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.datetime.now()
            if now.hour == 8 and now.minute == 0:
                for user_id, user_settings in self.settings.items():
                    anniversary_str = user_settings.get('anniversary', None)
                    if anniversary_str is not None:
                        anniversary = datetime.datetime.strptime(anniversary_str, '%d/%m/%Y').date()
                        days_since_anniversary = (datetime.date.today() - anniversary).days
                        message = f"Today is {datetime.date.today().strftime('%d %B %Y')}. It has been {days_since_anniversary} days since your anniversary!"
                        user = self.get_user(int(user_id))
                        if user is not None:
                            await user.send(message)
                # Wait for 24 hours before sending the message again
                await asyncio.sleep(24 * 60 * 60)
            else:
                # Check again in 1 minute
                await asyncio.sleep(60)

    async def get_anniversary(self, ctx):
        """Get your anniversary date"""
        user_id = str(ctx.author.id)
        if user_id in self.settings and 'anniversary' in self.settings[user_id]:
            anniversary = datetime.datetime.strptime(self.settings[user_id]['anniversary'], '%d/%m/%Y').date()
            await ctx.send(f"Your anniversary date is {anniversary.strftime('%d %B %Y')}")
        else:
            await ctx.send("You haven't set your anniversary date yet.")

# Replace YOUR_TOKEN_HERE with your bot's token
bot = DateBot()
bot.run()
