import discord
import config

from discord.ext import commands


class JogadorView(discord.ui.View):
    @discord.ui.select(
        custom_id='jogador_selector',
        min_values=0,
        max_values=8,
        placeholder='Selecione seus cargos',
        options=[
            discord.SelectOption(
                label='PC',
                value='pc',
                emoji='🖥️',
                description='Jogador(a) que joga ToF pelo computador'),
                
            discord.SelectOption(
                label='Mobile',
                value='mobile',
                emoji='📱',
                description='Jogador(a) que joga ToF pelo celular'),

            discord.SelectOption(
                label='Masculino',
                value='masculino',
                emoji='🙋‍♂️',
                description='Jogador do sexo masculino'),

            discord.SelectOption(
                label='Feminino',
                value='feminino',
                emoji='🙋🏼‍♀️',
                description='Jogador do sexo feminino'),

            discord.SelectOption(
                label='Heterosessual',
                value='heterosessual',
                emoji='👫🏼',
                description='Jogador(a) do gênero heterossexual'),

            discord.SelectOption(
                label='LGBTQIAP+',
                value='lgbt',
                emoji='👭🏼',
                description='Jogador(a) do gênero LGBTQIAP+'),

            discord.SelectOption(
                label='-18',
                value='menor',
                emoji='🔞',
                description='Jogador(a) menor de 18 anos'),

            discord.SelectOption(
                label='+18',
                value='maior',
                emoji='🧑🏼',
                description='Jogador(a) maior de 18 anos'),

            discord.SelectOption(
                label='CineAnime',
                value='cineanime',
                emoji='<:CineAnimes:1061749270430089376>',
                description='Jogador que quer assistir filmes/animes em chamadas'),

            discord.SelectOption(
                label='Mudae Player',
                value='mudae_player',
                emoji='<:UmaruHehe:1006618969882497064>',
                description='Jogador que quer acesso aos canais do Mudae bot'),
            
            discord.SelectOption(
                label='Dicas',
                value='dicas',
                emoji='<:UmaruHehe:1006618969882497064>',
                description='Jogador que quer acesso aos canais do Mudae bot'),

            discord.SelectOption(
                label='Novidades',
                value='novidades',
                emoji='<:UmaruHehe:1006618969882497064>',
                description='Jogador que quer acesso aos canais do Mudae bot'),
            ]
        )

    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True, thinking=True)

        pc = guild.get_role(config.pc)
        mobile = guild.get_role(config.mobile)
        masculino = guild.get_role(config.masculino)
        feminino = guild.get_role(config.feminino)
        hetero = guild.get_role(config.hetero)
        lgbt = guild.get_role(config.lgbt)
        menor = guild.get_role(config.menor)
        maior = guild.get_role(config.maior)
        cineanime = guild.get_role(config.cineanime)
        mudae_player = guild.get_role(config.mudae_player)

        roles_list = [pc, mobile, masculino, feminino, hetero,
                      lgbt, menor, maior, cineanime, mudae_player]
        values_list = ['pc', 'mobile', 'masculino', 'feminino',
                       'hetero', 'lgbt', 'menor', 'maior', 'cineanime', 'mudae_player']
        index_value = 0

        add = '**Adicionado:**'
        mantem = '**Mantido:**'
        removido = '**Removido:**'

        for role in roles_list:
            while index_value < len(roles_list)+1:
                if values_list[index_value] in select.values:
                    if roles_list[index_value] not in user.roles:
                        await user.add_roles(roles_list[index_value])
                        add += f'\n*+ {roles_list[index_value].mention}*'
                    else:
                        await user.remove_roles(roles_list[index_value])
                        removido += f'\n*- {roles_list[index_value].mention}*'
                else:
                    if roles_list[index_value] in user.roles:
                        mantem += f'\n*~ {roles_list[index_value].mention}*'
                index_value += 1
                break

        await interaction.edit_original_response(content=f'{"**Nenhum cargo adicionado**" if len(add)<17 else add}'
        f'\n\n{"**Nenhum cargo removido**" if len(removido)<17 else removido}'
        f'\n\n{"**Nenhum cargo mantido**" if len(mantem)<14 else mantem}')


class ClassView(discord.ui.View):
    @discord.ui.select(
        custom_id='class_selector',
        min_values=0,
        max_values=3,
        placeholder='Selecione sua classe',
        options=[
            discord.SelectOption(
                label='DPS',
                value='dps',
                emoji='⚔️',
                description='Membro que joga na função de DPS'),

            discord.SelectOption(
                label='TANK',
                value='tank',
                emoji='🛡️',
                description='Membro que joga na função de TANK'),

            discord.SelectOption(
                label='SUP',
                value='sup',
                emoji='❤️',
                description='Membro que joga na função de SUP')
            ]
        )   
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True, thinking=True)

        dps = guild.get_role(config.dps)
        tank = guild.get_role(config.tank)
        sup = guild.get_role(config.sup)

        membro = guild.get_role(config.membros)

        roles_list = [dps, tank, sup]
        values_list = ['dps', 'tank', 'sup']
        index_value = 0

        add = '**Adicionado:**'
        mantem = '**Mantido:**'
        removido = '**Removido:**'


        if membro not in user.roles:
            await interaction.edit_original_response(content=f'{user.mention}, você não é um {membro.mention} para ter acesso a esses cargos')
            return


        for role in roles_list:
            while index_value < len(roles_list)+1:
                if values_list[index_value] in select.values:
                    if roles_list[index_value] not in user.roles:
                        await user.add_roles(roles_list[index_value])
                        add += f'\n*+ {roles_list[index_value].mention}*'
                    else:
                        await user.remove_roles(roles_list[index_value])
                        removido += f'\n*- {roles_list[index_value].mention}*'
                else:
                    if roles_list[index_value] in user.roles:
                        mantem += f'\n*~ {roles_list[index_value].mention}*'
                index_value += 1
                break

        await interaction.edit_original_response(content=f'{"**Nenhum cargo adicionado**" if len(add)<17 else add}'
                                                 f'\n\n{"**Nenhum cargo removido**" if len(removido)<17 else removido}'
                                                 f'\n\n{"**Nenhum cargo mantido**" if len(mantem)<14 else mantem}')


class instanciaView(discord.ui.View):
    @discord.ui.select(
        custom_id='instancia_selector',
        min_values=0,
        max_values=7,
        placeholder='Selecione seus cargos',
        options=[
            discord.SelectOption(
                label='Chefe Mundial',
                value='chefe',
                emoji='👾',
                description='Membro que quer ser notificado quando marcarem este cargo'),

            discord.SelectOption(
                label='Fenda do Vazio',
                value='fenda',
                emoji='💀',
                description='Membro que quer ser notificado quando marcarem este cargo'),
            
            discord.SelectOption(
                label='Abismo Vazio',
                value='abismo',
                emoji='☠️',
                description='Membro que quer ser notificado quando marcarem este cargo'),

            discord.SelectOption(
                label='Embate Fronteiriço',
                value='embate',
                emoji='🗼',
                description='Membro que quer ser notificado quando marcarem este cargo'),

            discord.SelectOption(
                label='Exploração Interestelar',
                value='exploraçao',
                emoji='🌀',
                description='Membro que quer ser notificado quando marcarem este cargo'),

            discord.SelectOption(
                label='Incursão',
                value='incursao',
                emoji='🏴‍☠️',
                description='Membro que quer ser notificado quando marcarem este cargo'),
            
            discord.SelectOption(
                label='Operação Conjunta',
                value='operaçao',
                emoji='🏷️',
                description='Membro que quer ser notificado quando marcarem este cargo'),
            
            discord.SelectOption(
                label='Origem da Guerra',
                value='origem',
                emoji='🛡️',
                description='Membro que quer ser notificado quando marcarem este cargo'),
        ]
    )
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True, thinking=True)

        abismo = guild.get_role(config.abismo_do_vazio)
        chefe = guild.get_role(config.world_boss)
        fenda = guild.get_role(config.fenda_do_vazio)
        embate = guild.get_role(config.embate)
        exploraçao = guild.get_role(config.exploraçao_interstelar)
        incursao = guild.get_role(config.incursao)
        operaçao = guild.get_role(config.operaçao_conjunta)
        origem = guild.get_role(config.origem_da_guerra)

        membro = guild.get_role(config.membros)

        roles_list = [abismo, chefe, fenda, embate, exploraçao, incursao, operaçao, origem]
        values_list = ['abismo', 'chefe', 'fenda', 'embate', 'exploraçao', 'incursao', 'operaçao', 'origem']
        index_value = 0

        add = '**Adicionado:**'
        mantem = '**Mantido:**'
        removido = '**Removido:**'

        if membro not in user.roles:
            await interaction.edit_original_response(content=f'{user.mention}, você não é um {membro.mention} para ter acesso a esses cargos')
            return

        for role in roles_list:
            while index_value < len(roles_list)+1:
                if values_list[index_value] in select.values:
                    if roles_list[index_value] not in user.roles:
                        await user.add_roles(roles_list[index_value])
                        add += f'\n*+ {roles_list[index_value].mention}*'
                    else:
                        await user.remove_roles(roles_list[index_value])
                        removido += f'\n*- {roles_list[index_value].mention}*'
                else:
                    if roles_list[index_value] in user.roles:
                        mantem += f'\n*~ {roles_list[index_value].mention}*'
                index_value += 1
                break

        await interaction.edit_original_response(content=f'{"**Nenhum cargo adicionado**" if len(add)<17 else add}'
                                                 f'\n\n{"**Nenhum cargo removido**" if len(removido)<17 else removido}'
                                                 f'\n\n{"**Nenhum cargo mantido**" if len(mantem)<14 else mantem}')


class instanciaView2(discord.ui.View):
    @discord.ui.select(
        custom_id='instancia2_selector',
        min_values=0,
        max_values=3,
        placeholder='Selecione seus cargos',
        options=[
            discord.SelectOption(
                label='Kototáxi',
                value='kototaxi',
                emoji='🚕',
                description='Membro que quer ser notificado quando marcarem este cargo'),

            discord.SelectOption(
                label='Farm de Pesca/AFK',
                value='farm',
                emoji='🎴',
                description='Membro que quer ser notificado quando marcarem este cargo'),

            discord.SelectOption(
                label='PvP (Libertaçãodo Destino/Perigos Abissais)',
                value='pvp',
                emoji='🚨',
                description='Membro que quer ser notificado quando marcarem este cargo'),
            ]
        )
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True, thinking=True)

        kototaxi = guild.get_role(config.kototaxi)
        farm = guild.get_role(config.farm_afk_pesca)
        pvp = guild.get_role(config.pvp)
        
        roles_list = [kototaxi, farm, pvp]
        values_list = ['kototaxi', 'farm', 'pvp']
        index_value = 0

        add = '**Adicionado:**'
        mantem = '**Mantido:**'
        removido = '**Removido:**'

        for role in roles_list:
            while index_value < len(roles_list)+1:
                if values_list[index_value] in select.values:
                    if roles_list[index_value] not in user.roles:
                        await user.add_roles(roles_list[index_value])
                        add += f'\n*+ {roles_list[index_value].mention}*'
                    else:
                        await user.remove_roles(roles_list[index_value])
                        removido += f'\n*- {roles_list[index_value].mention}*'
                else:
                    if roles_list[index_value] in user.roles:
                        mantem += f'\n*~ {roles_list[index_value].mention}*'
                index_value += 1
                break

        await interaction.edit_original_response(content=f'{"**Nenhum cargo adicionado**" if len(add)<17 else add}'
                                                 f'\n\n{"**Nenhum cargo removido**" if len(removido)<17 else removido}'
                                                 f'\n\n{"**Nenhum cargo mantido**" if len(mantem)<14 else mantem}')


class CargosSelector(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.jogadorView = JogadorView(timeout=None)
        self.classView = ClassView(timeout=None)
        self.instancia1 = instanciaView(timeout=None)
        self.instancia2 = instanciaView2(timeout=None)

    async def cog_load(self):
        self.bot.add_view(self.jogadorView)
        self.bot.add_view(self.classView)
        self.bot.add_view(self.instancia1)
        self.bot.add_view(self.instancia2)
        

    @commands.command(name='view')
    @commands.is_owner()
    async def membros_view(self, ctx: commands.Context):
        ''' Inicia os seletores de cargos '''

        jogadorEmbed = discord.Embed(color=config.vermelho,
                                    description='Selecione os cargos que deseja: 🖥️ 📱 🙋‍♂️ 🙋🏼‍♀️')

        classEmbed = discord.Embed(color=config.vermelho,
                                   description='Selecione os cargos que deseja: ⚔️ 🛡️ ❤️')

        instancia1Embed = discord.Embed(color=config.vermelho,
                                        description='Selecione os cargos que deseja: ☠️ 👾 💀 🗼')

        instancia2Embed = discord.Embed(color=config.vermelho,
                                        description='Selecione os cargos que deseja: 🚕 🎴 🚨')

        await ctx.channel.send(embed=jogadorEmbed, view=JogadorView())
        await ctx.channel.send(embed=classEmbed, view=ClassView())
        await ctx.channel.send(embed=instancia1Embed, view=instanciaView())
        await ctx.channel.send(embed=instancia2Embed, view=instanciaView2())
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(CargosSelector(bot))