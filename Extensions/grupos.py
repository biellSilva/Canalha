import discord
import config
import time
import datetime
import re
import random
import asyncio

from discord import app_commands
from discord.ext import commands
from typing import Optional
from ast import literal_eval


class gruposCommand(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.incursao_view = IncursaoView(timeout=None)
        self.grupos_view = GruposView(timeout=None)

        self.lista_menu = app_commands.ContextMenu(
            name='Listar Membros do Grupo',
            callback=self.listagem
        )
        self.membro_menu = app_commands.ContextMenu(
            name='Adicionar Membro ao Grupo',
            callback=self.adicionar_membro
        )
        self.membro_menu_2 = app_commands.ContextMenu(
            name='Remover Membro do Grupo',
            callback=self.remover_membro
        )

        self.bot.tree.add_command(self.lista_menu)
        self.bot.tree.add_command(self.membro_menu)
        self.bot.tree.add_command(self.membro_menu_2)

    async def cog_load(self):
        self.bot.add_view(self.incursao_view)
        self.bot.add_view(self.grupos_view)

    async def cog_unload(self):
        self.bot.tree.remove_command(
            self.lista_menu.name, type=self.lista_menu.type)
        self.bot.tree.remove_command(
            self.membro_menu.name, type=self.membro_menu.type)
        self.bot.tree.remove_command(
            self.membro_menu_2.name, type=self.membro_menu_2.type)

    async def listagem(self, interaction: discord.Interaction, message: discord.Message):

        ''' Listar os Membros inscritos no grupo '''

        user = interaction.user
        guild = interaction.guild

        lider = guild.get_role(config.líder_incursor)
        admin = guild.get_role(config.admin)
        dev = guild.get_role(config.dev)

        if (lider not in user.roles) and (admin not in user.roles) and (dev not in user.roles):
            await interaction.response.send_message(f'Você não é um {lider.mention} ou {admin.mention}', ephemeral=True, delete_after=10)
            return

        embed = message.embeds[0]
        x = embed.fields[0].value.replace("\u200B", "")
        y = embed.fields[1].value.replace("\u200B", "")
        z = embed.fields[2].value.replace("\u200B", "")
        w = embed.fields[3].value.replace("\u200B", "")

        txt = f'DPS:{x}\n\n'
        txt += f'SUP:{y}\n\n'
        txt += f'TANK:{z}\n\n'
        txt += f'RESERVA:{w}'

        await interaction.response.send_message(f'```{txt}```', ephemeral=True)

    async def adicionar_membro(self, interaction: discord.Interaction, messagem: discord.Message):

        ''' Adiciona membro ao grupo '''

        user = interaction.user
        guild = interaction.guild
        admin = guild.get_role(config.admin)
        dev = guild.get_role(config.dev)
        embed = messagem.embeds
        x = []

        if admin not in user.roles and dev not in user.roles:
            await interaction.response.send_message(f'Você não é um {admin.mention}', ephemeral=True, delete_after=10)
            return

        for members in guild.members:
            x.append(members.mention)

        await interaction.response.send_message(f'Informe um membro e sua classe\nEx.: {random.choice(x)} dps, tank ou sup', ephemeral=True, delete_after=10)

        def check(message: discord.Message):
            return message.author == user

        response: discord.Message = await self.bot.wait_for('message', check=check)

        membro = response.mentions[0]
        cargo = response.content.split()[1]

        for field in embed[0].fields:
            if membro.mention in field.value:
                await interaction.followup.send(f'{membro.mention} já faz parte deste grupo como: {field.name}', ephemeral=True)
                await response.delete()
                return

        for field in embed[0].fields:
            if cargo.lower() in field.name.lower():
                if 'dps' in field.name.lower():
                    ind = 0
                if 'sup' in field.name.lower():
                    ind = 1
                if 'tank' in field.name.lower():
                    ind = 2

                if membro.mention not in field.value:
                    x = f'{field.value}\n{membro.mention}'
                    embed[0].set_field_at(ind, name=field.name, value=x)

                    embed[1].set_field_at(ind, name=embed[1].fields[ind].name, value=int(embed[1].fields[ind].value) - 1)

                    embed[0].set_field_at(4, name=embed[0].fields[4].name, value=int(embed[0].fields[4].value) - 1)

                    await messagem.edit(embeds=embed)
                    await interaction.followup.send(f'{membro.mention} adicionado como {field.name}', ephemeral=True)
                    await response.delete()
                    return

    async def remover_membro(self, interaction: discord.Interaction, messagem: discord.Message):

        ''' Remove o membro do grupo '''

        user = interaction.user
        guild = interaction.guild
        admin = guild.get_role(config.admin)
        dev = guild.get_role(config.dev)
        embed = messagem.embeds
        x = []

        if admin not in user.roles and dev not in user.roles:
            await interaction.response.send_message(f'Você não é um {admin.mention}', ephemeral=True, delete_after=10)
            return

        for members in guild.members:
            x.append(members.mention)

        await interaction.response.send_message(f'Informe um membro\nEx.: {random.choice(x)}', ephemeral=True, delete_after=10)

        def check(message):
            return message.author == user

        response: discord.Message = await self.bot.wait_for('message', check=check)
        membro = response.mentions[0]

        for field in embed[0].fields:
            if membro.mention in field.value:
                if 'dps' in field.name.lower():
                    ind = 0
                if 'sup' in field.name.lower():
                    ind = 1
                if 'tank' in field.name.lower():
                    ind = 2

                x = field.value.replace(f'\n{membro.mention}', '')
                embed[0].set_field_at(ind, name=field.name, value=x)

                z = int(embed[0].fields[4].value) + 1
                embed[0].set_field_at(4, name=embed[0].fields[4].name, value=z)

                embed[1].set_field_at(ind, name=embed[1].fields[ind].name, value=int(embed[1].fields[ind].value) + 1)

                await messagem.edit(embeds=embed)
                await response.delete()
                await interaction.followup.send(f'{membro.mention} foi removido da função: {field.name}', ephemeral=True)
                return

    grupos = app_commands.Group(name='grupos', description='Comandos para formar grupos', guild_only=True)

    @grupos.command(name='incursao')
    @app_commands.describe(data='Informe uma data, ex.: 22/12/2022 21:00:00',
                           nivel='Informe o nivel minimo necessario, ex.: 80',
                           objetivo='Informe o caminho da incursão, ex: apofis - frigg - nemesis',
                           titulo='Define um Título personalizado',
                           cor='Define uma cor personalizada, deve ser passado em HEX, ex.: #20B2AA',
                           oficial='Destinado a incursões OFICIAIS gerenciadas por um Admin')
    @app_commands.choices(
        oficial=[
            app_commands.Choice(name='8 Membros / 1 Grupo', value='8'),
            app_commands.Choice(name='16 Membros / 2 Grupos', value='16'),
            app_commands.Choice(name='24 Membros / 3 Grupos', value='24')])
    async def incursao(self, interaction: discord.Interaction, data: str, nivel: int, objetivo: str, oficial: Optional[str], titulo: Optional[str], cor: Optional[str]):

        ''' Monte seu grupo para Incursão '''

        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True, thinking=True)

        canal_oficial = guild.get_channel(config.inc_oficial)
        canal_clan = guild.get_channel(config.inc_clan)
        log = guild.get_channel(config.log)

        incursao = guild.get_role(config.incursao)
        lider = guild.get_role(config.líder_incursor)
        admin = guild.get_role(config.admin)
        dev = guild.get_role(config.dev)

        error_embed = discord.Embed(color=config.cinza,
                                    description='',
                                    timestamp=datetime.datetime.now(tz=config.tz_brazil))
        error_embed.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        if oficial:
            if admin not in user.roles and dev not in user.roles:
                error_embed.description = (f'Você não possui o cargo {admin.mention} para criar uma incursão oficial')
                await interaction.edit_original_response(embed=error_embed)
                return
            
        try:
            data = time.mktime(datetime.datetime.strptime(data, '%d/%m/%Y %H:%M').timetuple())
        except:
            try:
                data = time.mktime(datetime.datetime.strptime(f'{datetime.date.today()} {data}', '%Y-%m-%d %H:%M').timetuple())
            except:
                try:
                    data = time.mktime(datetime.datetime.strptime(f'{data} 21:00', '%d/%m/%Y %H:%M').timetuple())
                except:
                    error_embed.description=(f'Utilize um formato de data válido\n'
                                            '**Esperado:**\n'
                                            '`22/12/2022 21:00` - para dia e horario determinado\n'
                                            '`21:00` - para o horario determinado no dia atual\n'
                                            '`22/12/2022` - para as 21 horas do dia determinado\n\n'
                                            f'**Recebido:** {data}')
                    
                    await interaction.edit_original_response(embed=error_embed)
                    return
                
        if cor:
            if len(cor) == len('#20B2AA'):
                try:
                    cor = literal_eval(cor.replace(' ', '').replace('#', '0x'))
                except:
                    error_embed.description = ('**Utilize uma cor em HEX:**\n'
                                               f'**Esperado:** #20B2AA\n'
                                               f'**Recebido:** {cor}')
                    await interaction.edit_original_response(embed=error_embed)
                    return
            else:
                error_embed.description = ('**Utilize uma cor em HEX:**\n'
                                           f'**Esperado:** #20B2AA | Comprimento: {len("#20B2AA")}\n'
                                           f'**Recebido:** {cor} | Comprimento: {len(cor)}')
                await interaction.edit_original_response(embed=error_embed)
                return
        else:
            cor = config.vermelho

        if nivel > 80:
            nivel = 80

        tempo = int(data)
        grupos = int(tempo - 600)

        em = discord.Embed(title=f'INCURSÃO INDEPENDENTE [{nivel}]',
                           color=cor,
                           description=f'*A incursão se iniciará as <t:{tempo}:t> horas, no dia <t:{tempo}:D>, <t:{tempo}:R>*\n'
                           f'*A formação dos grupos começa as <t:{grupos}:t> horas, no dia <t:{grupos}:D>, <t:{grupos}:R>*\n\n'
                           f'Objetivo: **{objetivo}**\n\n'
                           f'{lider.mention} - {user.mention}\n\n')

        em.set_author(name=user, icon_url=user.display_avatar.url)
        em.add_field(name='<:RDPS:1035984602923286528>', value='\u200B')
        em.add_field(name='<:RSUP:1035984608572997752>', value='\u200B')
        em.add_field(name='<:RTANK:1035984611110551722>', value='\u200B')
        em.add_field(name='<:lgtv:1028478918400954458>', value='\u200B')

        if titulo:
            em.title = f'{titulo} [lvl: {nivel}]'

        em1 = discord.Embed(color=cor)

        if oficial:
            if oficial == '8':
                value = 8
                em1.add_field(name='Vagas DPS:', value=5)
                em1.add_field(name='Vagas SUP:', value=2)
                em1.add_field(name='Vagas TANK:', value=1)

            elif oficial == '16':
                value = 16
                em1.add_field(name='Vagas DPS:', value=10)
                em1.add_field(name='Vagas SUP:', value=4)
                em1.add_field(name='Vagas TANK:', value=2)

            elif oficial == '24':
                value = 24
                em1.add_field(name='Vagas DPS:', value=14)
                em1.add_field(name='Vagas SUP:', value=6)
                em1.add_field(name='Vagas TANK:', value=4)

            em.title = f'LISTA PREPARATÓRIA DA INCURSÃO OFICIAL [lvl: {nivel}]'
            em.description = (f'*A incursão se iniciará as <t:{tempo}:t> horas, no dia <t:{tempo}:D>, <t:{tempo}:R>*\n'
                              f'*A formação dos grupos começa as <t:{grupos}:t> horas, no dia <t:{grupos}:D>, <t:{grupos}:R>*\n\n'
                              f'Os membros abaixo estarão listados para os grupos de incursão e serão remanejados para os respectivos grupos de forma equilibrada tendo seus grupos formados e postados no dia da incursão:')

            em2 = discord.Embed(color=cor, description='**OBSERVAÇÕES:**\n'
                                '*1) Os membros do grupo que não puderem vir ou que vão se atrasar por algum motivo, favor avisar o encarregado pela Incursão.*\n'
                                '*2) O grupo será montado 10 minutos antes do horário marcado e começará no horário que foi determinado.*\n'
                                f'*3) Caso o horário chegue ao seu limite e os membros do grupo principal não estiverem presentes, o {lider.mention} dará sua vaga ao próximo na lista de reservas.*',
                                timestamp=datetime.datetime.now(tz=config.tz_brazil))
            em2.set_footer(text='Clique em um dos botões abaixo para entrar')

        else:
            value = 8
            em1.add_field(name='Vagas DPS:', value=5)
            em1.add_field(name='Vagas SUP:', value=2)
            em1.add_field(name='Vagas TANK:', value=1)

        em.add_field(name='Vagas:', value=value)

        if oficial:
            await canal_oficial.send(incursao.mention, embeds=[em, em1, em2], view=IncursaoView())
        else:
            await canal_clan.send(incursao.mention, embeds=[em, em1, em2], view=IncursaoView())

        resp = discord.Embed(color=config.cinza,
                             description=f'{"Incursão:" if oficial else "Incursao Oficial:"} **{em.title}** criada para <t:{tempo}:F>\n'
                                         f'Você se tornou um {lider.mention}, lembre-se de estar online às <t:{grupos}:t>',
                             timestamp=datetime.datetime.now(config.tz_brazil))
        resp.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        logEmbed = discord.Embed(color=config.verde,
                                 description=f'{user.mention} criou um grupo para {"incursão" if oficial else "incursao oficial"}\n'
                                 f'Titulo: **{em.title}**',
                                 timestamp=datetime.datetime.now(tz=config.tz_brazil))
        logEmbed.set_footer(text=f'{user} - {user.id}', icon_url=user.display_avatar.url)

        await user.add_roles(lider)
        await interaction.edit_original_response(embed=resp)
        await log.send(embed=logEmbed)
        return

    @grupos.command(name='outros')
    @app_commands.describe(nivel='Informe o nivel minimo necessario, ex.: 80',
                           objetivo='Informe o cargo referente a instância',
                           vagas='Informe quantas vagas o grupo deve ter')
    async def grupos_outros(self, interaction: discord.Interaction, objetivo: str, nivel: int, vagas: Optional[int]):

        ''' Crie grupos para o que desejar'''

        await interaction.response.defer(ephemeral=True, thinking=True)

        guild = interaction.guild
        user = interaction.user

        canal_clan = guild.get_channel(config.inc_clan)
        log = guild.get_channel(config.log)

        error_embed = discord.Embed(color=config.cinza,
                                    description='')
        error_embed.set_footer(text=user.display_name,
                               icon_url=user.display_avatar.url)

        try:
            cargo = guild.get_role(int(objetivo.replace('<', '').replace('>', '').replace('&', '').replace('@', '')))
        except ValueError:
            error_embed.description=(f'**Objetivo** deve ser uma menção de cargo')
            error_embed.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.edit_original_response(embed=error_embed)
            return

        if cargo.mentionable == False:
            error_embed.description = f'Pingar o cargo {cargo.mention} não é permitido'
            error_embed.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.edit_original_response(embed=error_embed)
            return
        
        em = discord.Embed(color=cargo.color,
                           description='Envie uma mensagem contendo o texto que deseja como descrição do seu grupo\n\n'
                           f'Use **c!cargo** em qualquer lugar na mensagem para que essa parte seja substituida pela menção do cargo {cargo.mention}\n\n'
                           'Use **c!leave** se deseja cancelar o comando',
                           timestamp=datetime.datetime.now(tz=config.tz_brazil))

        await interaction.edit_original_response(embed=em)

        def check(message: discord.Message):
            return message.author == interaction.user and message.channel == interaction.channel and message.content is not ''

        try:
            message: discord.Message = await self.bot.wait_for('message', check=check, timeout=180)
        except asyncio.TimeoutError:
            error_embed.description = 'O tempo de espera chegou ao fim, comando abortado'
            error_embed.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.edit_original_response(embed=error_embed)
            return

        if message.content.lower().startswith('c!leave'):
            await message.delete()
            error_embed.description = 'Comando cancelado pelo autor'
            error_embed.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.edit_original_response(embed=error_embed)
            return

        if 'c!cargo' in message.content.lower():
            message.content = message.content.replace('c!cargo', cargo.mention)

        em.description = message.content.capitalize()
        await message.delete()

        em.title = f'{cargo.name} [lvl: {nivel}]'
        em.set_footer(text=f'{user.display_name} - {user.id}', icon_url=user.display_avatar.url)
        em.add_field(name='Participantes', value='\u200B')

        if vagas:
            em.add_field(name='Vagas', value=vagas)

        await interaction.edit_original_response(content='Digite **confirmo** se o grupo está certo', embed=em)

        def check(message: discord.Message):
            return message.author == interaction.user and message.channel == interaction.channel and message.content == 'confirmo'

        try:
            message: discord.Message = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            error_embed.description = 'O tempo de espera chegou ao fim, comando abortado'
            error_embed.timestamp = datetime.datetime.now(tz=config.tz_brazil)
            await interaction.edit_original_response(content='', embed=error_embed)
            return
        
        if message.content.lower() == 'confirmo':
            await message.delete()
            await canal_clan.send(cargo.mention, embed=em, view=GruposView())

            error_embed.description = f'Grupo enviado para {canal_clan.mention}'
            await interaction.edit_original_response(content='', embed=error_embed)

            logEmbed = discord.Embed(color=config.verde,
                                     description=f'{user.mention} criou um grupo para {cargo.mention}\n'
                                     f'**Descrição:** \n{em.description}',
                                     timestamp=datetime.datetime.now(tz=config.tz_brazil))
            logEmbed.set_footer(text=f'{user} - {user.id}',icon_url=user.display_avatar.url)
            await log.send(embed=logEmbed)
            return



class GruposView(discord.ui.View):

    @discord.ui.button(custom_id='buttom_Entrar', label='ENTRAR', style=discord.ButtonStyle.grey)
    async def button_Entrar(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        user = interaction.user
        msg_edit = interaction.message
        embed = msg_edit.embeds

        em = discord.Embed(color=config.cinza,
                           description='',
                           timestamp=datetime.datetime.now(tz=config.tz_brazil))
        em.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        for field in embed[0].fields:
            if 'participantes' in field.name.lower():
                if user.mention in field.value:

                    embed[0].set_field_at(1, name=embed[0].fields[1].name, value=int(embed[0].fields[1].value) + 1)
                    embed[0].set_field_at(0, name=field.name, value=field.value.replace(f'\n{user.mention}', ''))
                    await msg_edit.edit(embeds=embed)

                    em.description = f'Você foi removido do grupo'
                    await interaction.response.send_message(embed=em, ephemeral=True, delete_after=10)
                    return

                else:
                    if int(embed[0].fields[1].value) <= 0:
                        em.description = f'Este grupo está cheio'
                        await interaction.response.send_message(embed=em, ephemeral=True, delete_after=10)
                        return

                    embed[0].set_field_at(0, name=field.name, value=f'{field.value}\n{user.mention}')
                    embed[0].set_field_at(1, name=embed[0].fields[1].name, value=int(embed[0].fields[1].value) - 1)
                    await msg_edit.edit(embeds=embed)

                    em.description = f'Você foi adicionado ao grupo'
                    await interaction.response.send_message(embed=em, ephemeral=True, delete_after=10)
                    return
                

    @discord.ui.button(custom_id='buttom_Delete', label='Delete', style=discord.ButtonStyle.grey, emoji='❌')
    async def button_DEL(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        lider = guild.get_role(config.líder_incursor)
        admin = guild.get_role(config.admin)
        dev = guild.get_role(config.dev)
        log = guild.get_channel(config.log)


        if (lider in user.roles) or (admin in user.roles) or (dev in user.roles):

            logEmbed = discord.Embed(color=config.vermelho,
                                     description=f'{user.mention} apagou um grupo\n'
                                     f'Criado por: {interaction.message.embeds[0].footer.text}\n'
                                     f'Titulo: {interaction.message.embeds[0].title}',
                                     timestamp=datetime.datetime.now(tz=config.tz_brazil))
            logEmbed.set_footer(text=f'{user} - {user.id}', icon_url=user.display_avatar.url)

            await interaction.message.delete()
            await user.remove_roles(lider)
            await interaction.response.send_message(f'{user.mention}, grupo apagado', ephemeral=True, delete_after=10)

            await log.send(embed=logEmbed)

        else:
            await interaction.response.send_message(f'{user.mention} você não é um {lider.mention}', ephemeral=True, delete_after=10)



class IncursaoView(discord.ui.View):

    @discord.ui.button(custom_id='buttom_DPS', label='DPS', style=discord.ButtonStyle.grey, emoji='<:RDPS:1035984602923286528>')
    async def button_DPS(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        user = interaction.user
        msg_edit = interaction.message
        embed = msg_edit.embeds

        for field in embed[0].fields:
            if user.mention in field.value:
                if buttom.label not in field.name:
                    await interaction.response.send_message(f'{user.mention}, você já faz parte da função: {field.name}', ephemeral=True, delete_after=10)
                    return

                else:
                    x = field.value.replace(f'\n{user.mention}', '')
                    embed[0].set_field_at(0, name=field.name, value=x)

                    z = int(embed[0].fields[4].value) + 1
                    embed[0].set_field_at(
                        4, name=embed[0].fields[4].name, value=z)

                    for field_vagas in embed[1].fields:
                        if buttom.label in field_vagas.name:
                            y = int(field_vagas.value) + 1
                            embed[1].set_field_at(
                                0, name=field_vagas.name, value=y)

                    await msg_edit.edit(embeds=embed)
                    await interaction.response.send_message(f'{user.mention}, você foi removido da função: {field.name}', ephemeral=True, delete_after=10)
                    return

        for field in embed[0].fields:
            if buttom.label in field.name:
                if int(embed[0].fields[4].value) <= 0:
                    await interaction.response.send_message(f'{user.mention}, este grupo não possui mais vagas.\n'
                                                            'Entre como reserva e será chamado caso algum membro não compareça', ephemeral=True, delete_after=10)
                    return

                for field_vagas in embed[1].fields:
                    if buttom.label in field_vagas.name:
                        if int(field_vagas.value) <= 0:
                            await interaction.response.send_message(f'{user.mention}, esta classe não possui mais vagas.\n'
                                                                    'Entre como reserva e será chamado caso algum membro não compareça', ephemeral=True, delete_after=10)
                            return

                x = field.value = f'{field.value}\n{user.mention}'
                embed[0].set_field_at(0, name=field.name, value=x)

                z = int(embed[0].fields[4].value) - 1
                embed[0].set_field_at(4, name=embed[0].fields[4].name, value=z)

                for field_vagas in embed[1].fields:
                    if buttom.label in field_vagas.name:
                        y = int(field_vagas.value) - 1
                        embed[1].set_field_at(
                            0, name=field_vagas.name, value=y)

                await msg_edit.edit(embeds=embed)
                await interaction.response.send_message(f'{user.mention}, você foi adicionado na função: {field.name}', ephemeral=True, delete_after=10)
                return

    @discord.ui.button(custom_id='buttom_SUP', label='SUP', style=discord.ButtonStyle.grey, emoji=':RSUP:1035984608572997752')
    async def button_SUP(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        user = interaction.user
        msg_edit = interaction.message
        embed = msg_edit.embeds

        for field in embed[0].fields:
            if user.mention in field.value:
                if buttom.label not in field.name:
                    await interaction.response.send_message(f'{user.mention}, você já faz parte da função: {field.name}', ephemeral=True, delete_after=10)
                    return

                else:
                    x = field.value.replace(f'\n{user.mention}', '')
                    embed[0].set_field_at(1, name=field.name, value=x)

                    z = int(embed[0].fields[4].value) + 1
                    embed[0].set_field_at(
                        4, name=embed[0].fields[4].name, value=z)

                    for field_vagas in embed[1].fields:
                        if buttom.label in field_vagas.name:
                            y = int(field_vagas.value) + 1
                            embed[1].set_field_at(
                                1, name=field_vagas.name, value=y)

                    await msg_edit.edit(embeds=embed)
                    await interaction.response.send_message(f'{user.mention}, você foi removido da função: {field.name}', ephemeral=True, delete_after=10)
                    return

        for field in embed[0].fields:
            if buttom.label in field.name:
                if int(embed[0].fields[4].value) <= 0:
                    await interaction.response.send_message(f'{user.mention}, este grupo não possui mais vagas.\n'
                                                            'Entre como reserva e será chamado caso algum membro não compareça', ephemeral=True, delete_after=10)
                    return

                for field_vagas in embed[1].fields:
                    if buttom.label in field_vagas.name:
                        if int(field_vagas.value) <= 0:
                            await interaction.response.send_message(f'{user.mention}, esta classe não possui mais vagas.\n'
                                                                    'Entre como reserva e será chamado caso algum membro não compareça', ephemeral=True, delete_after=10)
                            return

                x = field.value = f'{field.value}\n{user.mention}'
                embed[0].set_field_at(1, name=field.name, value=x)

                z = int(embed[0].fields[4].value) - 1
                embed[0].set_field_at(4, name=embed[0].fields[4].name, value=z)

                for field_vagas in embed[1].fields:
                    if buttom.label in field_vagas.name:
                        y = int(field_vagas.value) - 1
                        embed[1].set_field_at(
                            1, name=field_vagas.name, value=y)

                await msg_edit.edit(embeds=embed)
                await interaction.response.send_message(f'{user.mention}, você foi adicionado na função: {field.name}', ephemeral=True, delete_after=10)
                return

    @discord.ui.button(custom_id='buttom_TANK', label='TANK', style=discord.ButtonStyle.grey, emoji=':RTANK:1035984611110551722')
    async def button_TANK(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        user = interaction.user
        msg_edit = interaction.message
        embed = msg_edit.embeds

        for field in embed[0].fields:
            if user.mention in field.value:
                if buttom.label not in field.name:
                    await interaction.response.send_message(f'{user.mention}, você já faz parte da função: {field.name}', ephemeral=True, delete_after=10)
                    return

                else:
                    x = field.value.replace(f'\n{user.mention}', '')
                    embed[0].set_field_at(2, name=field.name, value=x)

                    z = int(embed[0].fields[4].value) + 1
                    embed[0].set_field_at(
                        4, name=embed[0].fields[4].name, value=z)

                    for field_vagas in embed[1].fields:
                        if buttom.label in field_vagas.name:
                            y = int(field_vagas.value) + 1
                            embed[1].set_field_at(
                                2, name=field_vagas.name, value=y)

                    await msg_edit.edit(embeds=embed)
                    await interaction.response.send_message(f'{user.mention}, você foi removido da função: {field.name}', ephemeral=True, delete_after=10)
                    return

        for field in embed[0].fields:
            if buttom.label in field.name:
                if int(embed[0].fields[4].value) <= 0:
                    await interaction.response.send_message(f'{user.mention}, este grupo não possui mais vagas.\n'
                                                            'Entre como reserva e será chamado caso algum membro não compareça', ephemeral=True, delete_after=10)
                    return

                for field_vagas in embed[1].fields:
                    if buttom.label in field_vagas.name:
                        if int(field_vagas.value) <= 0:
                            await interaction.response.send_message(f'{user.mention}, esta classe não possui mais vagas.\n'
                                                                    'Entre como reserva e será chamado caso algum membro não compareça', ephemeral=True, delete_after=10)
                            return

                x = field.value = f'{field.value}\n{user.mention}'
                embed[0].set_field_at(2, name=field.name, value=x)

                z = int(embed[0].fields[4].value) - 1
                embed[0].set_field_at(4, name=embed[0].fields[4].name, value=z)

                for field_vagas in embed[1].fields:
                    if buttom.label in field_vagas.name:
                        y = int(field_vagas.value) - 1
                        embed[1].set_field_at(
                            2, name=field_vagas.name, value=y)

                await msg_edit.edit(embeds=embed)
                await interaction.response.send_message(f'{user.mention}, você foi adicionado na função: {field.name}', ephemeral=True, delete_after=10)
                return

    @discord.ui.button(custom_id='buttom_AUX', label='RESERVA', style=discord.ButtonStyle.grey, emoji=':lgtv:1028478918400954458')
    async def button_AUX(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        user = interaction.user
        msg_edit = interaction.message
        embed = msg_edit.embeds

        for field in embed[0].fields:
            if user.mention in field.value:
                if 'lgtv' in field.name:
                    x = field.value.replace(f'\n{user.mention}', '')
                    embed[0].set_field_at(3, name=field.name, value=x)

                    await msg_edit.edit(embeds=embed)
                    await interaction.response.send_message(f'{user.mention}, você foi removido da função: {field.name}', ephemeral=True, delete_after=10)
                    return

                else:
                    await interaction.response.send_message(f'{user.mention}, você já faz parte da função: {field.name}', ephemeral=True, delete_after=10)
                    return

        for field in embed[0].fields:
            if 'lgtv' in field.name:
                embed[0].set_field_at(3, name=field.name, value=f'{field.value}\n{user.mention}')

                await msg_edit.edit(embeds=embed)
                await interaction.response.send_message(f'{user.mention}, você foi adicionado na função: {field.name}', ephemeral=True, delete_after=10)
                return

    @discord.ui.button(custom_id='buttom_DEL', label='Del', style=discord.ButtonStyle.grey, emoji='❌')
    async def button_DEL(self, interaction: discord.Interaction, buttom: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        lider = guild.get_role(config.líder_incursor)
        admin = guild.get_role(config.admin)
        dev = guild.get_role(config.dev)
        log = guild.get_channel(config.log)

        try:
            if interaction.message.embeds[2]:
                if admin in user.roles or dev in user.roles:
                    await interaction.message.delete()
                    await user.remove_roles(lider)
                    await interaction.response.send_message(f'{user.mention}, grupo apagado', ephemeral=True, delete_after=10)
                    logEmbed = discord.Embed(color=config.vermelho,
                                             description=f'{user.mention} apagou um grupo para incursão\n'
                                             f'Criado por: {interaction.message.embeds[0].author.name}\n'
                                             f'Titulo: {interaction.message.embeds[0].title}',
                                             timestamp=datetime.datetime.now(tz=config.tz_brazil))
                    logEmbed.set_author(
                        name=user, icon_url=user.display_avatar.url)
                    await log.send(embed=logEmbed)

                else:
                    await interaction.response.send_message(f'{user.mention}, você não é um {admin.mention} para poder apagar um grupo oficial', ephemeral=True, delete_after=10)

        except:
            if lider in user.roles or admin in user.roles or dev in user.roles:
                await interaction.message.delete()
                await user.remove_roles(lider)
                await interaction.response.send_message(f'{user.mention}, grupo apagado', ephemeral=True, delete_after=10)

                logEmbed = discord.Embed(color=config.vermelho,
                                         description=f'{user.mention} apagou um grupo para incursão\n'
                                         f'Criado por: {interaction.message.embeds[0].author.name}\n'
                                         f'Titulo: {interaction.message.embeds[0].title}',
                                         timestamp=datetime.datetime.now(tz=config.tz_brazil))
                logEmbed.set_author(
                    name=user, icon_url=user.display_avatar.url)

                await log.send(embed=logEmbed)

            else:
                await interaction.response.send_message(f'{user.mention} você não é um {lider.mention}', ephemeral=True, delete_after=10)



async def setup(bot):
    await bot.add_cog(gruposCommand(bot))
