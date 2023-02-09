import discord
import config
import wavelink

from discord.ext import commands
from typing import Optional


class Music(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.create_nodes())

    async def create_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='localhost',
                                            port='2333',
                                            password='discloud')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Wavelink Node: {node.identifier} ready')

    @commands.command(name='join', aliases=['connect', 'entre'])
    async def join(self, ctx: commands.Context, canal: Optional[discord.VoiceChannel]):
        if canal is None:
            canal = ctx.author.voice.channel

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is not None:
            if player.is_connected():
                return await ctx.send(canal.mention)

        await canal.connect(cls=wavelink.Player, timeout=30, self_deaf=True)
        await ctx.message.add_reaction(config.confirm)
    
    @commands.command(name='leave', aliases=['disconnect', 'saia'])
    async def leave(self, ctx: commands.Context):

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send('nao estou')
        
        await player.disconnect()
        await ctx.message.add_reaction(config.confirm)

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx: commands.Context, *, url):
        tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, url)

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, timeout=30, self_deaf=True)
        else:
            vc: wavelink.Player = ctx.voice_client

        await vc.set_volume(5)
        await vc.play(tracks[0])
        await ctx.message.add_reaction(config.confirm)

    @commands.command(name='search')
    async def search(self, ctx: commands.Context, *, search: str):
        search = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        await vc.set_volume(5)
        await vc.play(search)
        await ctx.message.add_reaction(config.confirm)

    @commands.command(name='stop')
    async def stop(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send('nao estou')
        
        if player.is_playing():
            await player.stop()
            return await ctx.message.add_reaction(config.confirm)
        else:
            await ctx.message.add_reaction(config.negative)

    @commands.command(name='pause')
    async def pause(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send('nao estou')
        
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                return await ctx.message.add_reaction(config.confirm)
            else:
                return await ctx.message.add_reaction(config.negative)
        else:
            return await ctx.message.add_reaction(config.negative)
        
    @commands.command(name='resume')
    async def resume(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send('nao estou')

        if player.is_paused():
            await player.resume()
            return await ctx.message.add_reaction(config.confirm)
        else:
            return await ctx.message.add_reaction(config.negative)
    
    @commands.command(name='volume')
    async def volume(self, ctx:commands.Context, volume: int):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        await player.set_volume(volume)
        return await ctx.message.add_reaction(config.confirm)
        
async def setup(bot):
    await bot.add_cog(Music(bot))
