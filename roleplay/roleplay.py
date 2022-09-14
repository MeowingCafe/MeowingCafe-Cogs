from redbot.core import commands, Config
import discord
import requests
import re
from string import Formatter

class Roleplay(commands.Cog):
	"""Use webhook for Role-Playing."""
	
	__author__ = "CafeMeowNeow"
	__version__ = "0.2.0"
	
	default_guild = {"webhooks": {}, "characters": {}}
	def __init__(self):
		self.config = Config.get_conf(self, identifier=2817739402)
		self.config.register_guild(**self.default_guild)


	@commands.group()
	async def roleplay(self, ctx: commands.Context):
		"""Control your role-playing experience."""

	@roleplay.group()
	async def execute(self, ctx: commands.Context):
		"""Execute user or character."""

	@execute.command(name="char")
	async def _char_execute(self, ctx: commands.Context, char_id: str, webhook_id: str, *, message):
		"""Execute a character for play."""
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
			webhook_dict = await self.config.guild(ctx.guild).webhooks()
			#this will change to use function link to set webhook_url
			webhook_url = webhook_dict[webhook_id]
			#await ctx.send(payload + webhook_url)
			send = requests.post(webhook_url, data=payload)

	@execute.command()
	async def member(self, ctx: commands.Context, char_name: discord.Member, webhook_id: str, *, message):
		"""Execute someone."""
		if char_name is not None:
			name = char_name.display_name
			avatar = str(char_name.avatar_url)
			payload = {
				'content': message,
				'username': name,
				'avatar_url': avatar
			}
			webhook_dict = await self.config.guild(ctx.guild).webhooks()
			#this will change to use function link to set webhook_url
			webhook_url = webhook_dict[webhook_id]
			#await ctx.send(payload + webhook_url)
			send = requests.post(webhook_url, data=payload)

	@roleplay.group()
	async def webhook(self, ctx: commands.Context):
		"""Manage webhooks."""

	@webhook.command(name="add")
	async def _add_webhook(self, ctx: commands.Context, webhook_id: str, *, webhook_url: str):
		"""Add a webhook."""
		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		webhook_dict.update({webhook_id: webhook_url})
		await self.config.guild(ctx.guild).webhooks.set(webhook_dict)

	@webhook.command(name="delete")
	async def _del_webhook(self, ctx: commands.Context, webhook_id: str):
		"""Delete a webhook."""
		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		del webhook_dict['webhook_id']
		await self.config.guild(ctx.guild).webhooks.set(webhook_dict)

	@webhook.command(name="list")
	async def _list_webhook(self, ctx: commands.Context):
		"""List Webhooks."""
		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		await ctx.send(webhook_dict)

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

	@char.command(name="delete")
	async def _del_char(self, ctx: commands.Context, char_id: str):
		"""Delete a character."""
		character_dict = await self.config.guild(ctx.guild).characters()
		del character_dict['char_id']
		await self.config.guild(ctx.guild).characters.set(character_dict)

	@char.command(name="list")
	async def _list_char(self, ctx: commands.Context):
		"""List characters."""
		character_dict = await self.config.guild(ctx.guild).characters()
		await ctx.send(character_dict)