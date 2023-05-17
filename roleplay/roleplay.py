import io
from asyncio import sleep
from string import Formatter
from typing import Union, Optional

import discord
import requests
import yaml

from redbot.core import commands, Config, checks
from redbot.core.bot import Red
from redbot.core.data_manager import cog_data_path


class Roleplay(commands.Cog):
	"""Use webhook for Role-Playing."""

	__author__ = "CafeMeowNeow"
	__version__ = "0.6.2"

	def __init__(self, bot: Red):
		self.bot = bot
		default_guild = {
			"webhooks": {},
			"characters": {}
		}
		default_member = {
			"interactive_perf": {
				"status": False
			}
		}
		self.config = Config.get_conf(self, identifier=2817739402)
		self.config.register_guild(**default_guild)
		self.config.register_member(**default_member)

	async def send(self, ctx: commands.Context, name: str, avatar: str, message: str, webhook: str):
		payload = {
			'content': message,
			'username': name,
			'avatar_url': avatar
		}
		#await ctx.send(payload + webhook_url)
		send = requests.post(webhook, data=payload)

	# async def webhook_check(self, guild: commands.Context.guild, webhook: Union[discord.TextChannel]):
	# 	webhook_dict = await self.config.guild(guild).webhooks()
	# 	for webhook_k in webhook_dict:
	# 		if webhook_k == str(webhook.id):
	# 			return True
	# 	return False


	@commands.Cog.listener()
	async def on_message(self, ctx: discord.Message):
		if ctx.author.bot:
			return
		for i in await self.bot.get_valid_prefixes(ctx.guild):
			if ctx.content.startswith(i):
				return

		perf_dict = await self.config.member(ctx.author).interactive_perf()
		if perf_dict["status"] is True:
			if perf_dict["backstage"] == ctx.channel.id:
				char_id = perf_dict["char_id"]
				webhook = perf_dict["webhook"]
				character_dict = await self.config.guild(ctx.guild).characters()
				char_info = character_dict[char_id]
				await self.send(ctx, char_info["username"], char_info["avatar_url"], ctx.content, webhook)

	@commands.group(aliases=["rph"])
	async def roleplay(self, ctx):
		"""Control your role-playing experience."""

	@roleplay.command(name="link", usage="<channel_OR_webhook>")
	@commands.guild_only()
	async def _link(self, ctx: commands.Context, webhook: Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread, str]):
		"""Set the default webhook to use when sending message."""
		if isinstance(webhook, (discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread, str)):
			webhook_dict = await self.config.guild(ctx.guild).webhooks()
			webhook_url = webhook_dict[str(webhook.id)]
		else:
			webhook_url = webhook

		perf_dict = await self.config.member(ctx.author).interactive_perf()
		perf_dict.update({"webhook": webhook_url})
		# await ctx.send(perf_dict)
		await self.config.member(ctx.author).interactive_perf.set(perf_dict)

	@roleplay.command(name="start", usage="<char_id> [backstage] [channel_OR_webhook]")
	@commands.guild_only()
	async def _perf_on(self, ctx: commands.Context, char_id: str, channel: Optional[discord.TextChannel], webhook: Optional[Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread, str]]):
		"""
		Start interactive performance.

		Will keep repost your message on a specific "backstage" channel.

		**Arguments:**
		`<char_id>` - The character used to send a message.
		`[backstage]` - The channel used to send your message.
		`[channel_OR_webhook]` - The receiving channel for your message.
		"""
		perf_dict = await self.config.member(ctx.author).interactive_perf()
		perf_dict.update({"status": True})
		perf_dict.update({"char_id": char_id})
		if webhook is not None:
			if isinstance(webhook, (discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread, str)):
				webhook_dict = await self.config.guild(ctx.guild).webhooks()
				webhook_url = webhook_dict[str(webhook.id)]
			else:
				webhook_url = webhook
			perf_dict.update({"webhook": webhook_url})

		if channel is not None:
			perf_dict.update({"backstage": channel.id})

		await self.config.member(ctx.author).interactive_perf.set(perf_dict)
		await ctx.send("*BUZZER NOISE*")

	@roleplay.command(name="stop")
	@commands.guild_only()
	async def _perf_off(self, ctx: commands.Context):
		"""Stop interactive performance."""
		perf_dict = await self.config.member(ctx.author).interactive_perf()
		perf_dict.update({"status": False})
		await self.config.member(ctx.author).interactive_perf.set(perf_dict)
		await ctx.send("SHOW IS OVER.")

	@roleplay.command(name="cast", usage="<char_id_OR_user> [channel] <message>")
	@commands.guild_only()
	async def _execute(self, ctx: commands.Context, char: Union[discord.Member, str], webhook: Optional[Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread]], *, message: str):
		"""
		Send message using character or user.

		Please use `\\` to escape quotes in the message.

		**Arguments:**
		`<char_id_OR_user>` - The character or user used to send a message.
		`[channel]` - The receiving channel for your message.
		"""
		if isinstance(char, discord.Member):
			name = char.display_name
			avatar_url = str(char.display_avatar)
		else:
			character_dict = await self.config.guild(ctx.guild).characters()
			try:
				char_info = character_dict[char]
			except KeyError as reason:
				await ctx.send("Invalid character or user.")
				return
			name = char_info["username"]
			avatar_url = char_info["avatar_url"]

		#await ctx.send(char_info)
		if webhook is None:
			perf_dict = await self.config.member(ctx.author).interactive_perf()
			webhook_url = perf_dict["webhook"]
		else:
			webhook_dict = await self.config.guild(ctx.guild).webhooks()
			webhook_url = webhook_dict[str(webhook.id)]
		await self.send(ctx, name, avatar_url, message, webhook_url)

	@roleplay.group()
	async def char(self, ctx):
		"""Manage characters."""

	@char.command(name="add", aliases=["create"], usage="<char_id> <name> <avatar_url>")
	@commands.guild_only()
	async def _add_char(self, ctx: commands.Context, char_id: str, username: str, avatar_url: str):
		"""
		Add a character for this server.

		You can use the image link on discord as an avatar.

		**Arguments:**
		`<char_id>` - The internal name of the character.
		`<name>` - The display name of the character.
		`<avatar_url>` - The url of character's avatar.
		"""
		character_dict = await self.config.guild(ctx.guild).characters()
		character_dict.update({char_id: {"username": username, "avatar_url": avatar_url}})
		await self.config.guild(ctx.guild).characters.set(character_dict)
		await ctx.send("Character {name} is created as {char_id}.".format(name=username, char_id=char_id))

	@char.command(name="delete", aliases=["del", "remove"])
	@commands.guild_only()
	async def _del_char(self, ctx: commands.Context, char_id: str):
		"""Delete a character on this server."""
		character_dict = await self.config.guild(ctx.guild).characters()
		del character_dict[char_id]
		await self.config.guild(ctx.guild).characters.set(character_dict)
		await ctx.send("Character deleted.")

	@char.command(name="list")
	@commands.guild_only()
	async def _list_char(self, ctx: commands.Context):
		"""List available characters on this server."""
		character_dict = await self.config.guild(ctx.guild).characters()
		await ctx.send(character_dict)
		# WIP

	@roleplay.command()
	async def playscript(self, ctx, script: str, webhook: Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread]):
		"""Play a script."""
		data_path = cog_data_path(self)
		guild_path = data_path.joinpath(str(ctx.message.guild.id))
		file_path = guild_path / f"{script}.yaml"

		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		webhook_url = webhook_dict[str(webhook.id)]

		file = open(file_path, 'rb')
		script = yaml.safe_load(file)
		lines = script['lines']
		for line in lines:
			chars = script['chars']
			char = line['char']
			await self.send(ctx, chars[char]['name'], chars[char]['avatar'], line['text'], webhook_url)
			await sleep(line['time'])

	@commands.group(aliases=["rphset"])
	async def roleplayset(self, ctx):
		"""Manage role-playing configurations."""	

	@roleplayset.group()
	async def webhook(self, ctx):
		"""Manage webhooks."""

	@webhook.command(name="add", aliases=["create"])
	@commands.guild_only()
	@checks.admin_or_permissions(manage_webhooks=True)
	async def _add_webhook(self, ctx: commands.Context, channel: Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread, str], webhook_url: str):
		"""Add a webhook for this server."""
		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		webhook_dict.update({channel.id: webhook_url})
		await self.config.guild(ctx.guild).webhooks.set(webhook_dict)
		await ctx.send("Webhook is associated with channel {channel} now.".format(channel=channel))

	@webhook.command(name="delete", aliases=["del", "remove"])
	@commands.guild_only()
	@checks.admin_or_permissions(manage_webhooks=True)
	async def _del_webhook(self, ctx: commands.Context, channel: Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread, str]):
		"""Delete a webhook on this server.."""
		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		del webhook_dict[str(channel.id)]
		await self.config.guild(ctx.guild).webhooks.set(webhook_dict)
		await ctx.send("Webhook deleted.")

	@webhook.command(name="list")
	@commands.guild_only()
	@checks.admin_or_permissions(manage_webhooks=True)
	async def _list_webhook(self, ctx: commands.Context):
		"""List available webhooks on this server."""
		webhook_dict = await self.config.guild(ctx.guild).webhooks()
		await ctx.send(webhook_dict)
		# WIP

	@roleplayset.command()
	@commands.guild_only()
	@checks.admin_or_permissions(manage_guild=True)
	async def clear(self, ctx, confirm: bool):
		"""
		Clear all configurations for this guild.

		Include characters, webhooks, and member settings.
		"""
		if confirm:
			await self.config.guild(ctx.guild).clear()
			await self.config.clear_all_members(ctx.guild)
			await ctx.send("ALL CLEAR!")

	@roleplayset.group()
	async def script(self, ctx):
		"""Manage scripts."""

	@script.command()
	@commands.guild_only()
	@checks.admin_or_permissions(manage_guild=True)
	async def upload(self, ctx):
		"""Upload script."""
		file = ctx.message.attachments[0]
		name = file.filename.rsplit(".", 1)[0].casefold()

		data_path = cog_data_path(self)
		guild_path = data_path.joinpath(str(ctx.message.guild.id))
		if not guild_path.exists():
			guild_path.mkdir()

		file_path = guild_path / f"{name}.yaml"
		#await ctx.send(file_path)
		b = io.BytesIO(await file.read())
		script = yaml.safe_load(b)
		b.seek(0)
		with file_path.open("wb") as p:
			p.write(b.read())