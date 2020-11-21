from redbot.core import commands
from redbot.cogs import audio
from json import loads
import re
class Wyyyy(commands.Cog):
    """Play song by netease music links!"""

    @commands.command()
    async def wyy(self, ctx, *, sharelink: str):
        """Play a netease music share link."""
        # Your code will go here
        if "song" in sharelink:
            rid = re.search(r'\?id=(\d*)', sharelink)
            if rid:
                url_best = "http://music.163.com/song/media/outer/url" + str(rid.group()) + ".mp3"
                play = ctx.bot.get_command("play")
                await ctx.invoke(play, query=url_best)
            else:
                await ctx.send("Can't find song id!")
        else:
            await ctx.send("This is not a song link!")