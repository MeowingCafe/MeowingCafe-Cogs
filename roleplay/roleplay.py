from email.policy import default
from redbot.core import commands, Config
import discord
import requests
import re


class Roleplay(commands.Cog):
	"""Use webhook for Role-Playing."""
	
	__author__ = "CafeMeowNeow"
	__version__ = "0.1.0"
	
	default_guild = {"default_webhook": ""}
	def __init__(self):
		self.config = Config.get_conf(self, identifier=2817739402)
		self.config.register_guild(**self.default_guild)
	

	@commands.command()
	async def roleplay(self, ctx: commands.Context, char_name: discord.Member = None, *, message):
		"""Start playing."""
		if char_name is not None:
			name = char_name.display_name
			avatar = str(char_name.avatar_url)
			payload = {
				'content': message,
				'username': name,
				'avatar_url': avatar
			}
			webhook_url = await self.config.default_webhook()
			#await ctx.send(payload + webhook_url)
			send = requests.post(webhook_url, data=payload)
			
	@commands.group()
	async def roleplayset(self, ctx: commands.Context):
		"""Roleplay settings."""

	@roleplayset.group()
	async def char(self, ctx: commands.Context):
		"""Manage characters."""

	@roleplayset.command()
	async def webhook(self, ctx: commands.Context, *, webhook_url: str):
		await self.config.default_webhook.set(webhook_url)