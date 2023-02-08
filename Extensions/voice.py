import discord
import config
import datetime
import asyncio
import youtube_dl
import re


from discord import app_commands
from discord.ext import commands, tasks
from typing import Optional


youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data: dict, volume=0.2):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.view = data.get('view_count')
        self.duration = str(datetime.timedelta(seconds=data.get("duration")))

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command()
    async def play(self, ctx: commands.Context, *, url: Optional[str]):
        '''Reproduz da URL'''

        embed = discord.Embed(color=config.cinza,
                                    description='')
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                embed.description = 'Você não está conectado a um canal de voz'
                return await ctx.send(embed=embed)

        voice_client: discord.VoiceClient = ctx.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            return await ctx.message.add_reaction(config.confirm)

        if url == None or not re.match(config.https_regex, url):
            embed.description = 'Informe um url válido'
            await ctx.send(embed=embed)
            return
        
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        embed.title = player.title
        embed.url = url
        embed.description = (f'**Duração:** {player.duration} || **Visualizações:** {player.view}')
        await ctx.send(embed=embed)

    @commands.command()
    async def volume(self, ctx: commands.Context, volume: Optional[int]):

        embed = discord.Embed(color=config.cinza,
                                    description='')
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        if volume is None:
            embed.description = f'Volume atual: {int(ctx.voice_client.source.volume)*10}%'
            return await ctx.send(embed=embed)

        if ctx.voice_client is None:
            embed.description = 'Não estou em um canal de voz'
            return await ctx.send(embed=embed)
        
        if ctx.voice_client.channel != ctx.author.voice.channel:
            embed.description = f'Você não está em {ctx.voice_client.channel.mention}'
            return await ctx.send(embed=embed)

        ctx.voice_client.source.volume = volume / 100
        await ctx.message.add_reaction(config.confirm)


    @commands.command()
    async def pause(self, ctx: commands.Context):

        if ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.message.add_reaction(config.negative)

        voice_client: discord.VoiceClient = ctx.voice_client

        if voice_client.is_paused():
            voice_client.resume()
            return await ctx.message.add_reaction(config.confirm)
        
        if voice_client.is_playing():
            voice_client.pause()
            return await ctx.message.add_reaction(config.confirm)
        

    @commands.command()
    async def leave(self, ctx: commands.Context):

        await ctx.voice_client.disconnect()
        ctx.voice_client.cleanup()
        return await ctx.message.add_reaction(config.confirm)



async def setup(bot):
    await bot.add_cog(Music(bot))
