from .wyyyy import Wyyyy


async def setup(bot):
    await bot.add_cog(Wyyyy())