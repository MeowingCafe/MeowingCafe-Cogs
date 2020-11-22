from redbot.core import commands
from redbot.cogs import audio
from json import loads
import json
import base64
import requests
import re
from Crypto.Cipher import AES
class Wyyyy(commands.Cog):
	"""Play song by netease music links!"""
	@commands.command()
	async def wyy(self, ctx, *, sharelink: str):
		"""Play a netease music share link."""
		# My code will go here
		if "song" in sharelink:
			rid = re.search(r'\?id=(\d*)', sharelink)
			if rid:
				#await ctx.send(rid)
				song_id = re.search(r'\d+',str(rid.group()))
				#await ctx.send(song_id)
				pubKey = "010001"
				modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
				nonce = "0CoJUm6Qyw8W8jud"
				def AES_encrypt(text, key, iv):
					pad = 16 - len(text) % 16
					text = text + pad * chr(pad)
					text = text.encode("utf-8")
					encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
					encrypt_text = encryptor.encrypt(text)
					encrypt_text = base64.b64encode(encrypt_text)
					return encrypt_text.decode('utf-8')
				def asrsea(p1, p2, p3, p4):
					res = {}
					rand_num = "aq9d7cvBOJ1tzj1o"
					vi = b"0102030405060708"
					h_encText = AES_encrypt(p1, p4, vi)
					h_encText = AES_encrypt(h_encText, rand_num, vi)
					res["encText"] = h_encText
					res["encSecKey"] = "5dec9ded1d7223302cc7db8d7e0428b04139743ab7e3d451ae47837f34e66f9a86f63e45ef20d147c33d88530a6c3c9d9d88e38586b42ee30ce43fbf3283a2b10e3118b76e11d6561d80e33ae38deb96832b1a358665c0579b1576b21f995829d45fc43612eede2ac243c6ebb6c2d16127742f3ac913d3ac7d6026b44cee424e"
					return res
				req = json.dumps({
					"ids": [song_id.group()],
					"br": 999000,
					"csrf_token": '',
					"level": "standard"
				})
				#await ctx.send(req)
				asrsea_res = asrsea(req, pubKey, modulus, nonce)
				param_data = {
					"params": asrsea_res["encText"],
					"encSecKey": asrsea_res["encSecKey"]
				}
				headers = {
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
					"Content-Type": "application/x-www-form-urlencoded",
					"Origin": "http://music.163.com",
					"Referer": "https://music.163.com",
					"Host": "music.163.com",
					"X-Real-IP": "27.38.4.87"
				}
				cookies = {"os": "ios"}
				songapi = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
				fucku = requests.post(songapi, headers=headers, data=param_data, verify=False, cookies=cookies)
				#await ctx.send(fucku.text)
				url_best = re.search(r'http.*\.mp3',fucku.text).group()
				#await ctx.send(url_best)
				#url_best = "http://music.163.com/song/media/outer/url" + str(rid.group()) + ".mp3"
				play = ctx.bot.get_command("play")
				await ctx.invoke(play, query = url_best)
			else:
				await ctx.send("Can't find song id!")
		else:
			await ctx.send("This is not a song link!")