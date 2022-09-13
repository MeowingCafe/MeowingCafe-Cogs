from redbot.core import commands, Config
import discord
import requests
import re
from string import Formatter

class Roleplay(commands.Cog):
	"""Use webhook for Role-Playing."""
	
	__author__ = "CafeMeowNeow"
	__version__ = "0.2.0"
	
	default_guild = {"webhook": {}, "characters": {}}
	def __init__(self):
		self.config = Config.get_conf(self, identifier=2817739402)
		self.config.register_guild(**self.default_guild)
	

	@commands.group()
	async def roleplay(self, ctx: commands.Context):
		"""Control your roleplay experience."""

	@roleplay.group()
	async def execute(self, ctx: commands.Context):
		"""Execute user or character."""
	
	@execute.command(name="char")
	async def _char_execute(self, ctx: commands.Context, char_id: str, webhook_name: str, *, message):
		"""Execute someone."""
		if char_id is not None:
			character_dict = await self.config.guild(ctx.guild).characters()
			char_info = character_dict[char_id]
			#await ctx.send(char_info)
			name = char_info["username"]
			avatar = char_info["avatar_url"]
			payload = {
				'content': message,
				'username': name,
				'avatar_url': avatar
			}
			webhook_dict = await self.config.guild(ctx.guild).webhook()
			#this will change to use function link to set webhook_url
			webhook_url = webhook_dict[webhook_name]
			#await ctx.send(payload + webhook_url)
			send = requests.post(webhook_url, data=payload)


	@execute.command()
	async def member(self, ctx: commands.Context, char_name: discord.Member, webhook_name: str, *, message):
		"""Execute someone."""
		if char_name is not None:
			name = char_name.display_name
			avatar = str(char_name.avatar_url)
			payload = {
				'content': message,
				'username': name,
				'avatar_url': avatar
			}
			webhook_dict = await self.config.guild(ctx.guild).webhook()
			#this will change to use function link to set webhook_url
			webhook_url = webhook_dict[webhook_name]
			#await ctx.send(payload + webhook_url)
			send = requests.post(webhook_url, data=payload)

	@roleplay.group()
	async def webhook(self, ctx: commands.Context):
		"""Manage webhooks."""

	@webhook.command(name="add")
	async def _add_webhook(self, ctx: commands.Context, webhook_name: str, *, webhook_url: str):
		webhook_dict = await self.config.guild(ctx.guild).webhook()
		webhook_dict.update({webhook_name: webhook_url})
		await self.config.guild(ctx.guild).webhook.set(webhook_dict)

	@roleplay.group()
	async def char(self, ctx: commands.Context):
		"""Manage characters."""

	@char.command(name="add")
	async def _add_char(self, ctx: commands.Context, char_id: str, username: str, avatar_url: str):
		"""Add a character."""
		character_dict = await self.config.guild(ctx.guild).characters()
		character_dict.update({char_id: {"username": username, "avatar_url": avatar_url}})
		await self.config.guild(ctx.guild).characters.set(character_dict)
		await ctx.send("Character {name} created as {chname}.".format(name=username, chname=char_id))
