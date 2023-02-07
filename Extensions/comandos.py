import discord
import config
import datetime
import time

from discord import app_commands
from discord.ext import commands
from typing import Optional


class AbertosCommand(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='avatar')
    @app_commands.describe(member='Selecione um membro')
    async def avatar(self, interaction: discord.Interaction, member: Optional[discord.Member]):

        ''' Envia o avatar/icone de um membro '''

        user = interaction.user

        if member == None:

            em = discord.Embed(color=config.branco if user.accent_color is None else user.accent_color)
            em.set_image(url=user.display_avatar)
            em.set_footer(text=f'Autor: {user}')
            em.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.response.send_message(embed=em)

        else:
            em = discord.Embed(color=config.branco if member.accent_color is None else member.accent_color)
            em.set_image(url=member.display_avatar)
            em.set_footer(text=f'Autor: {user}')
            em.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.response.send_message(embed=em)

    @commands.hybrid_command()
    async def tag(self, ctx: commands.Context, *, arg: Optional[str]):
        await ctx.send(arg)

    @commands.hybrid_command(name='unixtime', with_app_command=True)
    @app_commands.describe(data='Informe uma data, ex.: 22/12/2022 21:00')
    async def unixtime(self, ctx: commands.Context, *, data: Optional[str]):
        '''Converte data para segundos'''

        error_embed = discord.Embed(color=config.cinza,
                                    timestamp=datetime.datetime.now(tz=config.tz_brazil),
                                    description='')

        if not data:
            unixtime = int(time.time())

        else:
            try:
                unixtime = int(time.mktime(datetime.datetime.strptime(data, '%d/%m/%Y %H:%M').timetuple()))
            except:
                try:
                    unixtime = int(time.mktime(datetime.datetime.strptime(f'{datetime.date.today()} {data}', '%Y-%m-%d %H:%M').timetuple()))
                except:
                    try:
                        unixtime = int(time.mktime(datetime.datetime.strptime(f'{data} 21:00', '%d/%m/%Y %H:%M').timetuple()))
                    except:
                        error_embed.description=(f'Utilize um formato de data válido\n'
                                                '**Esperado:**\n'
                                                '`22/12/2022 21:00` - para dia e horario determinado\n'
                                                '`21:00` - para o horario determinado no dia atual\n'
                                                '`22/12/2022` - para as 21 horas do dia determinado\n\n'
                                                f'**Recebido:** {data}')
                        
                        await ctx.send(embed=error_embed)
                        return

        em = discord.Embed(color=config.cinza,
                           title='Discord Timestamps',
                           description=f'''
                               **Formatação:**
                               \<t:{unixtime}> - <t:{unixtime}>
                               \<t:{unixtime}:t> - <t:{unixtime}:t>
                               \<t:{unixtime}:T> - <t:{unixtime}:T>
                               \<t:{unixtime}:d> - <t:{unixtime}:d>
                               \<t:{unixtime}:D> - <t:{unixtime}:D>
                               \<t:{unixtime}:f> - <t:{unixtime}:f>
                               \<t:{unixtime}:F> - <t:{unixtime}:F>
                               \<t:{unixtime}:R> - <t:{unixtime}:R>
                               ''')

        await ctx.send(embed=em, ephemeral=True)



async def setup(bot):
    await bot.add_cog(AbertosCommand(bot))
