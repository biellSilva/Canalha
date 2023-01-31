import discord
import config
import datetime
import time
import json
import os


from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice
from typing import Optional


class AlertEvent(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_load(self):
        self.anuncio.start()

        if not os.path.exists('./json/mudae_alert.json'):
            with open('./json/mudae_alert.json', 'w') as f:
                json.dump({}, f,indent=4)

        if not os.path.exists('./json/mudae_wish.json'):
            with open('./json/mudae_wish.json', 'w') as f:
                json.dump({}, f, indent=4)

    def cog_unload(self):
        self.anuncio.stop()

    @tasks.loop(minutes=1)
    async def anuncio(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(config.avalon)
        mudae_chat = guild.get_channel(config.mudae_chat)

        if datetime.datetime.now(tz=config.tz_brazil).minute == 23:

            tempo = int(time.time()) + 300
            users = ''

            mudae_alert = await get_mudae_alert_data()
            lista_rolls: list = mudae_alert[str(guild.id)]['rolls']
            lista_claim: list = mudae_alert[str(guild.id)]['claim']

            mudae_rolls = guild.get_channel(config.mudae_rolls)

            em = discord.Embed(color=config.cinza,
                               description=f'Reset de rolls <t:{tempo}:R>, a seus postos {mudae_rolls.mention}',
                               timestamp=datetime.datetime.now(tz=config.tz_brazil))
            em.set_footer(text=guild.name, icon_url=guild.icon.url)

            if datetime.datetime.now(tz=config.tz_brazil).hour in (0, 3, 6, 9, 12, 15, 18, 21):
                for user_claim in lista_claim:
                    if user_claim not in lista_rolls:
                        lista_rolls.append(user_claim)

                em = discord.Embed(color=config.vermelho,
                                   description=f'Reset de rolls e claim <t:{tempo}:R>, a seus postos {mudae_rolls.mention}',
                                   timestamp=datetime.datetime.now(tz=config.tz_brazil))
                em.set_footer(text=guild.name, icon_url=guild.icon.url)

            for user in lista_rolls:
                users += f' {guild.get_member(user).mention}'

            await mudae_chat.send(content=users, embed=em)
            

    @commands.hybrid_group(name='mudae', with_app_command=True)
    @app_commands.choices(
        comando=[
            Choice(name='Ajuda', value='help'),
            Choice(name='Lista', value='list')
        ])
    async def mudae(self, ctx: commands.Context, comando: Optional[str]):
        ''' Painel de informações '''

        if comando == None:
            ''' Embed do usuario '''
            series = await get_mudae_wish_data()
            alertas = await get_mudae_alert_data()

            em = discord.Embed(color=config.cinza,
                               description='')
            em.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            
            em.description += 'Sua Wish Série:\n'
            for serie in series[str(ctx.guild.id)]:
                if ctx.author.id in series[str(ctx.guild.id)][serie]:
                    em.description += f'{serie.title()}\n'
            
            em.description += '\nSeus Alertas:\n'
            for alerta in alertas[str(ctx.guild.id)]:
                if ctx.author.id in alertas[str(ctx.guild.id)][alerta]:
                    em.description += f'{alerta.title()} - 🔔\n'
                else:
                    em.description += f'{alerta.title()} - 🔕\n'

            await ctx.send(embed=em)
            return
        

        if comando.lower() == 'help':
            ''' Embed de ajuda '''

            em = discord.Embed(color=config.cinza,
                               description='''Mudae Help: \n
                               **c!mudae** - Painel do usuario
                               **c!mudae list** - Server Wish List
                               **c!mudae help** - Painel de ajuda
                               **c!mudae wish**  - Alerta da série
                               **c!mudae alerta** - Alerta de Claim/Rolls''')

            await ctx.send(embed=em)
            return
        

        if comando.lower() == 'list':
            ''' Embed listando todos wish series '''

            series = await get_mudae_wish_data()

            em = discord.Embed(color=config.cinza, description='Server Wish List: \n\n')
            for serie in series[str(ctx.guild.id)]:
                users_count = len(series[str(ctx.guild.id)][serie])
                em.description += f'**{serie.title()}** - {users_count} {"participante" if users_count == 1 else "participantes"}\n'

            await ctx.send(embed=em)
            return


    @mudae.command(name='alerta', with_app_command=True)
    @app_commands.describe(alerta='Escolha qual alerta do Mudae deseja ativar/desativar')
    @app_commands.choices(
        alerta=[
            Choice(name='Alerta Roll', value='rolls'),
            Choice(name='Alerta Claim', value='claim')
        ])
    async def alerta(self, ctx: commands.Context, alerta: str):

        ''' Configure seus alertas do Mudae bot '''

        alerta = alerta.lower()
        guild = ctx.guild
        user = ctx.author

        if alerta not in ('rolls', 'claim'):
            em = discord.Embed(color=config.cinza,
                               description=f'Error: **{alerta}** não é um argumento válido\n'
                                            'Esperado: **c!mudae alerta rolls/claim**')
            em.set_footer(text=user.display_name, icon_url=user.avatar.url)
            await ctx.send(embed=em, ephemeral=True)
            return

        await mudae_alert_json(guild)
        mudae_alert = await get_mudae_alert_data()

        if alerta == 'rolls':
            if user.id not in mudae_alert[str(guild.id)]['rolls']:

                x: list = mudae_alert[str(guild.id)]['rolls']
                x.append(user.id)
                mudae_alert[str(guild.id)]['rolls'] = x

                with open('./json/mudae_alert.json', 'w') as f:
                    json.dump(mudae_alert, f, indent=4)

                em = discord.Embed(color=config.cinza,
                                  description=f'Adicionado ao alerta de rolls\n')
                em.set_footer(text=user.display_name, icon_url=user.avatar.url)

            else:
                x: list = mudae_alert[str(guild.id)]['rolls']
                x.remove(user.id)
                mudae_alert[str(guild.id)]['rolls'] = x

                with open('./json/mudae_alert.json', 'w') as f:
                    json.dump(mudae_alert, f, indent=4)

                em = discord.Embed(color=config.cinza,
                                   description=f'Removido do alerta de rolls')
                em.set_footer(text=user.display_name, icon_url=user.avatar.url)

        if alerta == 'claim':
            if user.id not in mudae_alert[str(guild.id)]['claim']:

                x: list = mudae_alert[str(guild.id)]['claim']
                x.append(user.id)
                mudae_alert[str(guild.id)]['claim'] = x

                with open('./json/mudae_alert.json', 'w') as f:
                    json.dump(mudae_alert, f, indent=4)

                em = discord.Embed(color=config.cinza,
                                   description=f'Adicionado ao alerta de claim')
                em.set_footer(text=user.display_name, icon_url=user.avatar.url)

            else:
                x: list = mudae_alert[str(guild.id)]['claim']
                x.remove(user.id)
                mudae_alert[str(guild.id)]['claim'] = x

                with open('./json/mudae_alert.json', 'w') as f:
                    json.dump(mudae_alert, f, indent=4)

                em = discord.Embed(color=config.cinza,
                                   description=f'{user.mention}, você foi removido do alerta de claim')
                em.set_footer(text=user.display_name, icon_url=user.avatar.url)

        await ctx.send(embed=em, ephemeral=True)

    
    @alerta.error
    async def alerta_error(self, ctx: commands.Context, err):

        em = discord.Embed(color=config.vermelho, description=err)
        em.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)

        if isinstance(err, commands.errors.MissingRequiredArgument):
            em.description = ('Error: Falta de argumento\n'
                              'Esperado: **c!mudae alerta rolls/claim**')
            
        await ctx.send(embed=em, ephemeral=True)
        print(err)
        return


    @mudae.command(name='wish', with_app_command=True)
    @app_commands.describe(serie='Nome da série/anime que deseja ser alertado')
    async def wish(self, ctx: commands.Context, *, serie: str):
        '''Wish Series'''

        guild = ctx.guild
        user = ctx.author

        em = discord.Embed(color=config.cinza, description='')
        em.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        await mudae_wish_json(guild)
        series = await get_mudae_wish_data()

        serie = serie.lower()

        if serie not in series[str(guild.id)]:
            try:
                await user.send('')
            except Exception as err:
                if isinstance(err, discord.errors.Forbidden):
                    await ctx.send('Não foi possivel enviar DM test para você, acesse suas configurações de privacidade neste servidor e permita essa configuração para que assim eu possa lhe notificar quando um personagem de sua serie surgir', ephemeral=True)
                    return
            
            series[str(guild.id)][serie.lower()] = [user.id]

            em.description = f'Adicionado a notificações de **{serie.title()}**'

        else:
            if user.id not in series[str(guild.id)][serie]:
                try:
                    await user.send('')
                except Exception as err:
                    if isinstance(err, discord.errors.Forbidden):
                        await ctx.send('Não foi possivel enviar DM test para você, acesse suas configurações de privacidade neste servidor para permitir, assim posso me notificar quando um personagem de sua serie surgir', ephemeral=True)
                        return

                users: list = series[str(guild.id)][serie]
                users.append(user.id)
                series[str(guild.id)][serie] = users

                em.description=f'Adicionado a notificações de **{serie.title()}**'

            else:
                users: list = series[str(guild.id)][serie]
                users.remove(user.id)
                series[str(guild.id)][serie] = users

                em.description = f'Removido da notificações de **{serie.title()}**'

        if len(series[str(guild.id)][serie]) == 0:
            x: dict = series[str(guild.id)]
            x.pop(serie, None)

            series[str(guild.id)] = x

        with open('./json/mudae_wish.json', 'w') as f:
            json.dump(series, f, indent=4)  

        await ctx.send(embed=em, ephemeral=True)
    
    @wish.error
    async def wish_error(self, ctx: commands.Context, err):
        em = discord.Embed(color=config.vermelho, description=err)
        em.set_footer(text=ctx.author.display_name,
                      icon_url=ctx.author.avatar.url)

        if isinstance(err, commands.errors.MissingRequiredArgument):
            em.description = ('Error: Falta de argumento\n'
                              'Esperado: **c!mudae wish <nome da serie>**')
            await ctx.send(embed=em)
        print(err)
        return  

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ''' Alerta de wish '''
        
        if (message.author.id != config.mudae_bot) or (message.channel.id != config.mudae_rolls):
            return
        
        if (len(message.embeds) == 0) or (message.embeds[0].footer.icon_url is not None):
            return
        
        guild = message.guild
        
        em = message.embeds[0].copy()
        em.url = message.jump_url
        em.title = 'Ir a mensagem'

        series = await get_mudae_wish_data()

        for serie in series[str(guild.id)]:
            if serie in message.embeds[0].description.lower():
                for user in series[str(guild.id)][serie]:
                    em.description = f'**{em.author.name}** da sua wish serie:\n**{serie}**\napareceu em {message.channel.mention}'
                    user = guild.get_member(user)
                    try:
                        await user.send(embed=em)
                    except:
                        return


# -------------------------------------------------------


async def mudae_alert_json(guild: discord.Guild):

    ''' Cria uma nova guilda no alerta do mudae '''

    mudae_alert = await get_mudae_alert_data()

    if str(guild.id) in mudae_alert:
        return False

    else:
        mudae_alert[str(guild.id)] = {}
        mudae_alert[str(guild.id)]['rolls'] = []
        mudae_alert[str(guild.id)]['claim'] = []

    with open('./json/mudae_alert.json', 'w') as f:
        json.dump(mudae_alert, f, indent=4)
        return True


async def get_mudae_alert_data():

    ''' Lê todo o arquivo mudae alert json '''

    with open('./json/mudae_alert.json', 'r') as f:
        mudae_alert = json.load(f)
    return mudae_alert


# -------------------------------------------------------


async def mudae_wish_json(guild: discord.Guild):

    ''' Entra no wish alerta do mudae '''

    mudae_wish = await get_mudae_wish_data()

    if str(guild.id) in mudae_wish:
        return False

    else:
        mudae_wish[str(guild.id)] = {}

    with open('./json/mudae_wish.json', 'w') as f:
        json.dump(mudae_wish, f, indent=4)
        return True


async def get_mudae_wish_data():

    ''' Lê todo o arquivo mudae wish json '''

    with open('./json/mudae_wish.json', 'r') as f:
        mudae_wish = json.load(f)
    return mudae_wish


async def setup(bot):   
    await bot.add_cog(AlertEvent(bot))
