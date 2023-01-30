import discord
import config
import datetime

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


async def setup(bot):
    await bot.add_cog(AbertosCommand(bot))
