#########################
#                       #
#  Бот создан: _Vadok_  #
#                       #
#########################


#libraies
import disnake
from disnake.ext import commands
from disnake import TextInputStyle, utils, Message
from mcrcon import MCRcon
import asyncio
from aiohttp import ClientSession
import requests
import re
import time
from settings import *

#Bot
intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="&", intents=intents)

apiKey = apiKey

skin_channel = skin_channel

server_name = server_name


ip = ip
port = port
password = password


#functions
def remove_color_codes(text: str) -> str:
    pattern = re.compile(r'§[0-9-a-fA-F]')
    return re.sub(pattern, '', text)

async def add_to_whitelist(username):
    with MCRcon(ip, password, port=port) as mcr:
        result = mcr.command(f'whitelist add {username}')
        return result

async def add_to_fwhitelist(floodgate_uuid):
    with MCRcon(ip, password, port=port) as mcr:
        result = mcr.command(f'fwhitelist add {floodgate_uuid}')
        return result

async def remwhitelist_player(username):
    with MCRcon(ip, password, port=port) as mcr:
        result = mcr.command(f'whitelist remove {username}')
        return result

async def ban_player(username):
    with MCRcon(ip, password, port=port) as mcr:
        result = mcr.command(f'ban {username}')
        return result

async def pardon_player(username):
    with MCRcon(ip, password, port=port) as mcr:
        result = mcr.command(f'pardon {username}')
        return result

async def set_skin(name, url):
    with MCRcon(ip, password, port=port) as mcr:
        result = mcr.command(f'skin set {name} {url}')
        return result

#Events
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)


#Modal Window
class MyModal(disnake.ui.Modal):
    def __init__(self):

        components = [
                disnake.ui.TextInput(
                   label="Ник",
                    placeholder="Введите свой ник",
                    custom_id="Ник:",
                    style=TextInputStyle.short,
                    max_length=20,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="Сколько вам лет?",
                    placeholder="Введите свой возраст",
                    custom_id="Возраст:",
                    style=TextInputStyle.short,
                    max_length=4,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="Чем хотите заняться?",
                    placeholder="Чем хотите заняться?",
                    custom_id="Занятие:",
                    style=TextInputStyle.long,
                    max_length=300,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="От кого узнали о нас?",
                    placeholder="От кого узнали?",
                    custom_id="От кого:",
                    style=TextInputStyle.short,
                    max_length=20,
                    required=True,
                ),
                disnake.ui.TextInput(
                    label="Java или Bedrock?",
                    placeholder="Java или Bedrock",
                    custom_id="Платформа:",
                    style=TextInputStyle.short,
                    max_length=10,
                    required=True,
                ),
            ]
        super().__init__(title=f"Заявка на {server_name}", components=components, timeout=180)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.send_message("Вы успешно подали заявку! После рассмотрения вы получите уведомление в личные сообщения.", ephemeral = True)

        autor = inter.author.id

        embed = disnake.Embed(title="\____НОВАЯ ЗАЯВКА____", color=disnake.Colour.green())
        for key, value in inter.text_values.items():
            embed.add_field(
                name=key.capitalize(),
                value=value[:1024],
                inline=False,
            )
        embed.add_field(name="Отправитель:", value=f"<@{autor}>", inline=True)
        embed.add_field(name="ID", value=autor, inline=False)

        moder_channel = bot.get_channel(admins_channel)
        await moder_channel.send(embed=embed, components=[
            disnake.ui.Button(label="Принять", style=disnake.ButtonStyle.green, custom_id="YES"),
            disnake.ui.Button(label="Отклонить", style=disnake.ButtonStyle.red, custom_id="NO"),
            disnake.ui.Button(label="Бедрок", style=disnake.ButtonStyle.gray, custom_id="Bedrock"),

            ],
        )


#commands
@bot.slash_command(name="application", description="Отправляет сообщение для подачи заявки.")
@commands.has_permissions(administrator=True)
async def buttons(inter: disnake.ApplicationCommandInteraction):
    embid = disnake.Embed(title=f"Заявка на {server_name}", colour=0xDC134C)
    embid.add_field(name="Что делать?", value="""Чтобы подать завку нужно нажать на кнопку ниже, в появившемся окне заполнить все необходимые данные, **ПОМНИ! Введённый ник должен быть __абсолютно точный__!**
""" , inline=False)
    embid.add_field(name="Я подал заявку, что дальше?", value="В таком случае тебе нужно просто ждать ответ в личных сообщениях!", inline=False)
    embid.add_field(name='Мою заявку одобрили, но когда я хочу зайти вижу "You are not whitelisted from this server!"', value="""
Если так случилось создай обращение в канале <#1056107711953109053>
Тебе обязательно помогут!""", inline=False)
    application_channel_id = inter.channel.id
    application_channel = bot.get_channel(application_channel_id)
    await application_channel.send(
        embed = embid,
        components=[
            disnake.ui.Button(label="--------------> Подать заявку <--------------", style=disnake.ButtonStyle.success, custom_id="zayavka"),
        ],
    )
    await inter.response.send_message ('Отправлено', ephemeral=True)

@bot.slash_command(name="очистить", description="Удаляет сообщения в чате.")
@commands.has_permissions(administrator=True)
async def clear(inter: disnake.ApplicationCommandInteraction, amount):
    await inter.response.send_message(f"Готово! Очищено {int(amount)} сообщений!", ephemeral=True)
    await inter.channel.purge(limit=int(amount))

@bot.slash_command(name="whitelist", description="Добавляет пользователя в белый список.")
@commands.has_permissions(administrator=True)
async def whitelist(ctx, username):
    try:
        result = await asyncio.wait_for(add_to_whitelist(username), timeout=10.0)
        await ctx.send(f'**{username}** добавлен в белый список!')
    except asyncio.TimeoutError:
        await ctx.send('Время ожидания истекло.')
    except Exception as e:
        await ctx.send(f'Произошла ошибка: {e}')

@bot.slash_command(name="remwhitelist", description="Удаляет пользователя из белого списка.")
@commands.has_permissions(administrator=True)
async def remwhitelist(ctx, username):
    try:
        result = await asyncio.wait_for(remwhitelist_player(username), timeout=10.0)
        await ctx.send(f'**{username}** удалён из белого списка!')
    except asyncio.TimeoutError:
        await ctx.send('Время ожидания истекло.')
    except Exception as e:
        await ctx.send(f'Произошла ошибка: {e}')

@bot.slash_command(name='ban', description="Блокирует пользователя на сервере")
@commands.has_permissions(administrator=True)
async def ban(ctx, username):
    try:
        result = await asyncio.wait_for(ban_player(username), timeout=10.0)
        await ctx.send(f'**{username}** отправлен в БАН!')
    except asyncio.TimeoutError:
        await ctx.send('Время ожидания истекло.')
    except Exception as e:
        await ctx.send(f'Произошла ошибка: {e}')

@bot.slash_command(name='pardon', description="Разблокирует пользователя на сервере.")
@commands.has_permissions(administrator=True)
async def pardon(ctx, username):
    try:
        result = await asyncio.wait_for(pardon_player(username), timeout=10.0)
        await ctx.send(f'**{username}** разБАНен!')
    except asyncio.TimeoutError:
        await ctx.send('Время ожидания истекло.')
    except Exception as e:
        await ctx.send(f'Произошла ошибка: {e}')

@bot.slash_command(
    name='skin',
    description='Устанавливает скин на сервере'
)
async def skin(inter: disnake.ApplicationCommandInteraction, name, url):
    channel = inter.channel.id

    if inter.channel.id == skin_channel:
        await inter.response.defer()

        try:
            result = await asyncio.wait_for(set_skin(name, url), timeout=10.0)
            str_result = str(result)
            cleaned_response = remove_color_codes(str_result)
            otvet = (f"Скин установлен!")
            await inter.edit_original_response(content=otvet)
            await asyncio.sleep(10)
            await inter.delete_original_response()

        except asyncio.TimeoutError:
            otvet = ('Время ожидания истекло.')
            await inter.edit_original_response(content=otvet)

        except Exception as e:
            otvet = (f'Произошла ошибка: {e}')
            await inter.edit_original_response(content=otvet)

    else:
        await inter.response.send_message(f'Доступно только в канале <#1056105529098903673>', ephemeral=True)


#Listen buttons
@bot.listen("on_button_click")
async def help_listener(inter: disnake.MessageInteraction):

    if inter.component.custom_id not in ["zayavka"]:
        return

    if inter.component.custom_id == "zayavka":
        await inter.response.send_modal(modal=MyModal())

@bot.listen("on_button_click")
async def help_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["YES", "NO", "Bedrock"]:
        return

    if inter.component.custom_id == "YES":

        username = inter.message.embeds[0].fields[0].value
        age = inter.message.embeds[0].fields[1].value
        idea = inter.message.embeds[0].fields[2].value
        inviter = inter.message.embeds[0].fields[3].value
        platform = inter.message.embeds[0].fields[4].value
        customer = inter.message.embeds[0].fields[5].value
        user_id = inter.message.embeds[0].fields[6].value
        message = inter.message
        int_user = int(user_id)
        judge = inter.user.display_name
        user = await bot.fetch_user(int_user)

        success_embed = disnake.Embed(title=f"ОДОБРЕНО {judge}", color=disnake.Colour.green())
        success_embed.add_field(name='Ник:', value=username, inline=False)
        success_embed.add_field(name='Возраст:', value=age, inline=False)
        success_embed.add_field(name='Занятие:', value=idea, inline=False)
        success_embed.add_field(name='От кого:', value=inviter, inline=False)
        success_embed.add_field(name='Платформа:', value=platform, inline=False)
        success_embed.add_field(name='Отправитель:', value=customer, inline=False)
        success_embed.add_field(name='ID:', value=user_id, inline=False)

        await inter.response.defer()

        await user.send(f"""Здравствуйте **<@{user_id}>**
Поздравляю! Ваша заявка на {server_name} одобрена!
Всю необходимую информацию вы можете найти в канале <#1041765722147258419>!
**Приятной игры!**""")

        await message.edit("Сообщение отправлено, добавление в белый список...")
        await add_to_whitelist(username)

        arhive_channel = bot.get_channel(archive_channel)
        await arhive_channel.send(embed=success_embed)

        response = (f"Заявка **{username}** одобрена!")
        await inter.edit_original_response(content=response)


    if inter.component.custom_id == "NO":

        user_id = inter.message.embeds[0].fields[6].value
        username = inter.message.embeds[0].fields[0].value
        age = inter.message.embeds[0].fields[1].value
        idea = inter.message.embeds[0].fields[2].value
        inviter = inter.message.embeds[0].fields[3].value
        platform = inter.message.embeds[0].fields[4].value
        customer = inter.message.embeds[0].fields[5].value
        user_id = inter.message.embeds[0].fields[6].value
        message = inter.message
        int_user = int(user_id)
        judge = inter.user.display_name
        user = await bot.fetch_user(int_user)

        rejected_embed = disnake.Embed(title=f"ОТКЛОНЕНО {judge}", color=disnake.Colour.red())
        rejected_embed.add_field(name='Ник:', value=username, inline=False)
        rejected_embed.add_field(name='Возраст:', value=age, inline=False)
        rejected_embed.add_field(name='Занятие:', value=idea, inline=False)
        rejected_embed.add_field(name='От кого:', value=inviter, inline=False)
        rejected_embed.add_field(name='Платформа:', value=platform, inline=False)
        rejected_embed.add_field(name='Отправитель:', value=customer, inline=False)
        rejected_embed.add_field(name='ID:', value=user_id, inline=False)

        await inter.response.defer()

        await user.send(f"""Здравствуйте **<@{user_id}>**
К сожалению ваша заявка на {server_name} отклонена(
Не расстраивайтесь, ведь вы можете подать заявку в следующий раз!""")

        arhive_channel = bot.get_channel(archive_channel)
        await arhive_channel.send(embed=rejected_embed)

        response = (f"Заявка **{username}** отклонена!")
        await inter.edit_original_response(content=response)


    if inter.component.custom_id == "Bedrock":
        username = inter.message.embeds[0].fields[0].value
        age = inter.message.embeds[0].fields[1].value
        idea = inter.message.embeds[0].fields[2].value
        inviter = inter.message.embeds[0].fields[3].value
        platform = inter.message.embeds[0].fields[4].value
        customer = inter.message.embeds[0].fields[5].value
        user_id = inter.message.embeds[0].fields[6].value
        message = inter.message
        int_user = int(user_id)
        judge = inter.user.display_name
        user = await bot.fetch_user(int_user)
        url = f'https://mcprofile.io/api/v1/bedrock/gamertag/{username}'
        headers = {
            'x-api-key': apiKey
        }

        success_embed = disnake.Embed(title=f"ОДОБРЕНО {judge}", color=disnake.Colour.green())
        success_embed.add_field(name='Ник:', value=username, inline=False)
        success_embed.add_field(name='Возраст:', value=age, inline=False)
        success_embed.add_field(name='Занятие:', value=idea, inline=False)
        success_embed.add_field(name='От кого:', value=inviter, inline=False)
        success_embed.add_field(name='Платформа:', value=platform, inline=False)
        success_embed.add_field(name='Отправитель:', value=customer, inline=False)
        success_embed.add_field(name='ID:', value=user_id, inline=False)

        await inter.response.defer()

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            floodgate_uuid = data['floodgateuid']

            await user.send(f"""Здравствуйте **<@{user_id}>**
Поздравляю! Ваша заявка на {server_name} одобрена!
Всю необходимую информацию вы можете найти в канале <#1041765722147258419>!
**Приятной игры!**""")

            await message.edit("Сообщение отправлено, добавление в белый список...")
            await add_to_fwhitelist(floodgate_uuid)

            arhive_channel = bot.get_channel(archive_channel)
            await arhive_channel.send(embed=success_embed)

            response = (f"Заявка **{username}** одобрена!")
            await inter.edit_original_response(content=response)
        else:
            response = (f"FUID **{username}** не получен! Похоже у бота проблема с сетью или у игрока нет Xbox аккаунта!")
            await inter.edit_original_response(content=response)

#Start
bot.run(bot_token)