import discord
import config
import datetime

from discord.ext import commands


class onMember(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild: discord.Guild = self.bot.get_guild(config.avalon)
        visitante = guild.get_role(config.visitante)
        log = guild.get_channel(config.member_log)

        if member.bot:
            return

        em = discord.Embed(color=config.verde,
                        description=f'{member.mention} entrou, cargo {visitante.mention} adicionado',
                        timestamp=datetime.datetime.now(tz=config.tz_brazil))
        em.set_footer(text=f'{member.display_name} - {member.id}')
        em.set_author(name= member, icon_url=member.display_avatar.url)

        await member.add_roles(visitante)
        await log.send(embed=em)


    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        log = guild.get_channel(config.member_log)

        member = payload.user
        
        if member.bot:
            return

        em = discord.Embed(color=config.vermelho,
                        description=f'{member.mention} saiu',
                        timestamp=datetime.datetime.now(tz=config.tz_brazil))
        em.set_footer(text=f'{member.display_name} - {member.id}')
        em.set_author(name=member, icon_url=member.display_avatar.url)

        await log.send(embed=em)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild: discord.Guild = self.bot.get_guild(config.avalon)
        log = guild.get_channel(config.log)

        if member.bot:
            return

        if after.channel is not None:
            em = discord.Embed(color=config.verde,
                            description=f'{member.mention} entrou no canal {after.channel.mention}')
            
        if before.channel is not None and after.channel is not None:
            if before.channel.id == after.channel.id:
                return

            em = discord.Embed(color=config.amarelo,
                               description=f'{member.mention} trocou do canal {before.channel.mention} para {after.channel.mention}')

        if after.channel is None:
            em = discord.Embed(color=config.vermelho,
                            description=f'{member.mention} saiu do canal {before.channel.mention}')

        em.timestamp = datetime.datetime.now(tz=config.tz_brazil)
        em.set_footer(text=f'{member.display_name} - {member.id}')
        em.set_author(name=member, icon_url=member.display_avatar.url)

        await log.send(embed=em)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        guild: discord.Guild = self.bot.get_guild(config.avalon)
        log = guild.get_channel(config.log)

        if message.author.bot:
            return

        em = discord.Embed(color=config.vermelho,
                            description=f'{message.author.mention} apagou uma mensagem em {message.channel.mention}\n'
                            f'**Mensagem deletada:**\n'
                            f'{message.content}',
                            timestamp=datetime.datetime.now(tz=config.tz_brazil))
        
        em.set_footer(text=f'{message.author.display_name} - {message.author.id}', icon_url=message.author.display_avatar.url)
        await log.send(embed=em)



    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        guild: discord.Guild = self.bot.get_guild(config.avalon)
        log = guild.get_channel(config.log)

        if message_before.author.bot:
            return

        if message_after.content == message_before.content:
            return

        em = discord.Embed(color=config.amarelo,
                           description=f'{message_before.author.mention} editou uma mensagem em {message_before.channel.mention}\n'
                           f'**Mensagem antes:**\n'
                           f'{message_before.content}\n\n'
                           f'**Mensagem depois:**\n'
                           f'{message_after.content}',
                        timestamp=datetime.datetime.now(tz=config.tz_brazil))
        em.set_footer(text=f'{message_before.author.display_name} - {message_before.author.id}', icon_url=message_before.author.display_avatar.url)
        await log.send(embed=em)


async def setup(bot):
    await bot.add_cog(onMember(bot))
