from redbot.core import commands, Config
import discord
import requests
import re
from string import Formatter

class Roleplay(commands.Cog):
	"""Use webhook for Role-Playing."""
	
	__author__ = "CafeMeowNeow"
	__version__ = "0.5.0"
	
	default_guild = {"webhooks": {}, "characters": {}}
	default_member = {"interactive_perf": {"status": False}}
	def __init__(self):
		self.config = Config.get_conf(self, identifier=2817739402)
		self.config.register_guild(**self.default_guild)
		self.config.register_member(**self.default_member)

	async def send(self, guild: commands.Context.guild, author: commands.Context.author, name: str, avatar: str, message: str, webhook_url: str = None):
		payload = {
			'content': message,
			'username': name,
			'avatar_url': avatar
		}
		if webhook_url is None:
			webhook_dict = await self.config.guild(guild).webhooks()#!
			perf_dict = await self.config.member(author).interactive_perf()#!
			webhook_url = perf_dict["webhook"]
		#await ctx.send(payload + webhook_url)
		send = requests.post(webhook_url, data=payload)

	async def webhook_check(self, webhook: str):
		webhook_dict = await self.config.guild(guild).webhooks()#!
		for webhook_k, webhook_v in webhook_dict:
			if webhook_k == webhook:
				return True
		return False


	@commands.Cog.listener()
	async def on_message(self, message: discord.Message):
		author = message.author
		guild = message.guild
		channel = message.channel.id
		perf_dict = await self.config.member(author).interactive_perf()
		if perf_dict["status"] is True:
			if perf_dict["backstage"] == channel:
				char_id = perf_dict["char_id"]
				webhook_id = perf_dict["webhook"]
				character_dict = await self.config.guild(guild).characters()
				char_info = character_dict[char_id]
				await self.send(guild, author, char_info["username"], char_info["avatar_url"], message, webhook_id)

	@commands.group()
	async def roleplay(self, ctx: commands.Context):
		"""Control your role-playing experience."""

	@roleplay.command(name="link")
	async def _link(self, ctx: commands.Context, webhook_id_or_url: str):
		"""Link a webhook."""
		is_url = None
		is_url = re.search(r'^http(s?)://', webhook_id_or_url)
		perf_dict = await self.config.member(ctx.author).interactive_perf()
		if is_url:
			perf_dict.update({"webhook": webhook_id_or_url})
		else:
			webhook_dict = await self.config.guild(ctx.guild).webhooks()
			webhook_url = webhook_dict[webhook_id_or_url]
			perf_dict.update({"webhook": webhook_url})
		# await ctx.send(perf_dict)
		await self.config.member(ctx.author).interactive_perf.set(perf_dict)

	@roleplay.command(name="start")
	async def _perf_on(self, ctx: commands.Context, char_id: str = None, webhook: str = None, channel: discord.TextChannel = None):
		"""Start interactive performance."""
		perf_dict = await self.config.member(ctx.author).interactive_perf()
		perf_dict.update({"status": True})
		if char_id is not None:
			perf_dict.update({"char_id": char_id})
		if webhook is not None:
			is_url = None
			is_url = re.search(r'^http(s?)://', webhook)
			if is_url:
				perf_dict.update({"webhook": webhook})
			else:
				webhook_dict = await self.config.guild(ctx.guild).webhooks()
				webhook_url = webhook_dict[webhook]
				perf_dict.update({"webhook": webhook_url})
		if channel is not None:
			perf_dict.update({"backstage": channel.id})
		await self.config.member(ctx.author).interactive_perf.set(perf_dict)

	@roleplay.command(name="stop")
	async def _perf_off(self, ctx: commands.Context):
		"""Stop interactive performance."""
		perf_dict = await self.config.member(ctx.author).interactive_perf()
		perf_dict.update({"status": False})
		await self.config.member(ctx.author).interactive_perf.set(perf_dict)

	@roleplay.group()
	async def execute(self, ctx: commands.Context):
		"""Execute user or character."""

	@execute.command(name="char")
	async def _char_execute(self, ctx: commands.Context, char_id: str, webhook_id: str, *, message):
		"""Execute a character for play."""
		character_dict = await self.config.guild(ctx.guild).characters()
		char_info = character_dict[char_id]
		#await ctx.send(char_info)
		if await webhook_check(webhook_id):
			await self.send(ctx.guild, ctx.author, char_info["username"], char_info["avatar_url"], message, webhook_id)
		else:
			await self.send(ctx.guild, ctx.author, char_info["username"], char_info["avatar_url"], webhook_id + message)
		

	@execute.command()
	async def member(self, ctx: commands.Context, member_name: discord.Member, webhook_id: str, *, message):
		"""Execute someone."""
		if await webhook_check(webhook_id):
			await self.send(ctx.guild, ctx.author, member_name.display_name, str(member_name.avatar_url), message, webhook_id)
		else:
			await self.send(ctx.guild, ctx.author, member_name.display_name, str(member_name.avatar_url), webhook_id + message)

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
		del webhook_dict[webhook_id]
		await self.config.guild(ctx.guild).webhooks.set(webhook_dict)

	@webhook.command(name="list")
	async def _list_webhook(self, ctx: commands.Context):
		"""List webhooks."""
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
		del character_dict[char_id]
		await self.config.guild(ctx.guild).characters.set(character_dict)

	@char.command(name="list")
	async def _list_char(self, ctx: commands.Context):
		"""List characters."""
		character_dict = await self.config.guild(ctx.guild).characters()
		await ctx.send(character_dict)