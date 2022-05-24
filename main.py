import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext.commands import CommandNotFound
import json
import asyncio
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import random

bot = commands.Bot(command_prefix="||")
bot.remove_command("help")
slash = SlashCommand(bot, sync_commands = True)

@bot.event
async def on_ready():
    print("Бот запущен:")
    print("Имя бота: ", bot.user.name)
    print("User ID: ", bot.user.id)

@slash.slash(name = 'help', description = 'Как открыть тикет?', guild_ids = [350817461328805888])
# @bot.command()
async def help(ctx):
    with open("data.json") as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if ctx.author.guild_permissions.administrator or valid_user:

        em = discord.Embed(title="CenturyTicket", description="", color=0x00a8ff)
        em.add_field(name="`/ticket <message>`", value="Это создаст новый билет. Добавьте любые слова после команды, если вы хотите отправить сообщение, когда мы изначально создадим ваш билет.")
        em.add_field(name="`/close`", value="Используйте это, чтобы закрыть заявку. Эта команда работает только в каналах тикетов.")
        em.add_field(name="`||addaccess <role_id>`", value="Это можно использовать, чтобы предоставить определенной роли доступ ко всем билетам. Эта команда может быть запущена только в том случае, если у вас есть роль администратора для этого бота.")
        em.add_field(name="`||delaccess <role_id>`", value="Это может быть использовано для удаления доступа определенной роли ко всем билетам. Эта команда может быть запущена только в том случае, если у вас есть роль администратора для этого бота.")
        em.add_field(name="`||addpingedrole <role_id>`", value="Эта команда добавляет роль в список ролей, которые проверяются при создании нового билета. Эта команда может быть запущена только в том случае, если у вас есть роль администратора для этого бота.")
        em.add_field(name="`||delpingedrole <role_id>`", value="Эта команда удаляет роль из списка ролей, которые проверяются при создании нового билета. Эта команда может быть запущена только в том случае, если у вас есть роль администратора для этого бота.")
        em.add_field(name="`||addadminrole <role_id>`", value="Эта команда предоставляет всем пользователям с определенной ролью доступ к командам уровня администратора для бота, таким как `.addpingedrole` и `.addaccess`. Эта команда может быть запущена только пользователями, имеющими права администратора для всего сервера.")
        em.add_field(name="`||deladminrole <role_id>`", value="Эта команда удаляет доступ для всех пользователей с указанной ролью к командам уровня администратора для бота, таким как `.addpingedrole` и `.addaccess`. Эта команда может быть запущена только пользователями, имеющими права администратора для всего сервера.")
        em.set_footer(text="Reload by BazZziliuS")

        await ctx.send(embed=em)
    
    else:

        em = discord.Embed(title = "CenturyTicket", description ="", color = 0x00a8ff)
        em.add_field(name="`/ticket <краткое описание>`", value="Это создаст новый тикет. Добавьте любые слова после команды, если вы хотите отправить сообщение, сразу в Ваш тикет.")
        em.set_footer(text="Reload by BazZziliuS")

        await ctx.send(embed=em)

@slash.slash(name = 'ticket', description = 'Открыть тикет', guild_ids = [350817461328805888])
# @bot.command()
async def ticket(ctx, *, args = None):

    await bot.wait_until_ready()

    if args == None:
        message_content = "Пожалуйста, подождите, мы скоро будем с вами!"
    
    else:
        message_content = "".join(args)

    with open("data.json") as f:
        data = json.load(f)

    ticket_number = int(data["ticket-counter"])
    ticket_number += 1

    ticket_channel = await ctx.guild.create_text_channel("тикет-{}".format(ticket_number))
    await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

    for role_id in data["valid-roles"]:
        role = ctx.guild.get_role(role_id)

        await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
    
    await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)

    em = discord.Embed(title="Новый тикет от {}".format(ctx.author), description= "{}".format(message_content), color=0x00a8ff)

    await ticket_channel.send(embed=em)

    pinged_msg_content = "Вызываю "
    non_mentionable_roles = []

    if data["pinged-roles"] != []:

        for role_id in data["pinged-roles"]:
            role = ctx.guild.get_role(role_id)

            pinged_msg_content += role.mention
            pinged_msg_content += " "

            if role.mentionable:
                pass
            else:
                await role.edit(mentionable=True)
                non_mentionable_roles.append(role)
        
        await ticket_channel.send(pinged_msg_content)

        for role in non_mentionable_roles:
            await role.edit(mentionable=False)
    
    data["ticket-channel-ids"].append(ticket_channel.id)

    data["ticket-counter"] = int(ticket_number)
    with open("data.json", 'w') as f:
        json.dump(data, f)
    
    created_em = discord.Embed(title="CenturyTicket", description="<@{}>, Ваш билет был создан по адресу {}".format(ctx.author.id, ticket_channel.mention), color=0x00a8ff)
    
    await ctx.send(embed=created_em)
    # await ctx.message.delete()

@slash.slash(name = 'close', description = 'Закрыть тикет', guild_ids = [350817461328805888])
# @bot.command()
async def close(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        if ctx.channel.id in data["ticket-channel-ids"]:

            channel_id = ctx.channel.id

            em = discord.Embed(title="CenturyTicket", description=f"Тикет будет закрыт оператором {ctx.author} через 1 минуту. \nЕсли Вам нужна все еще помощь откройте новый тикет.", color=0x00a8ff)
        
            await ctx.send(embed=em)
            await asyncio.sleep(60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)
    else:
        eme = discord.Embed(title="CenturyTicket", description=f"Закрыть тикет может только операторо.", color=0x00a8ff)
        await ctx.send(embed=eme, delete_after=20)


        

@bot.command()
async def addaccess(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:
        role_id = int(role_id)

        if role_id not in data["valid-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["valid-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                em = discord.Embed(title="CenturyTicket", description="Вы успешно добавили `{}` к списку ролей с доступом к билетам.".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="CenturyTicket", description="Это недопустимый идентификатор роли. Пожалуйста, повторите попытку с действительным идентификатором роли.")
                await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="CenturyTicket", description="Эта роль уже имеет доступ к билетам!", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="CenturyTicket", description="Извините, у вас нет разрешения на выполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def delaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            valid_roles = data["valid-roles"]

            if role_id in valid_roles:
                index = valid_roles.index(role_id)

                del valid_roles[index]

                data["valid-roles"] = valid_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="CenturyTicket", description="Вы успешно удалили `{}` из списка ролей, имеющих доступ к билетам.".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)
            
            else:
                
                em = discord.Embed(title="CenturyTicket", description="У этой роли уже нет доступа к билетам!", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="CenturyTicket", description="Это недопустимый идентификатор роли. Пожалуйста, повторите попытку с действительным идентификатором роли.")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="CenturyTicket", description="Извините, у вас нет разрешения на выполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def addpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        role_id = int(role_id)

        if role_id not in data["pinged-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["pinged-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="CenturyTicket", description="Вы успешно добавили `{}` к списку ролей, которые проверяются при создании новых билетов!".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="CenturyTicket", description="Это недопустимый идентификатор роли. Пожалуйста, повторите попытку с действительным идентификатором роли.")
                await ctx.send(embed=em)
            
        else:
            em = discord.Embed(title="CenturyTicket", description="Эта роль уже получает запросы при создании билетов.", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="CenturyTicket", description="Извините, у вас нет разрешения на выполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
async def delpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            pinged_roles = data["pinged-roles"]

            if role_id in pinged_roles:
                index = pinged_roles.index(role_id)

                del pinged_roles[index]

                data["pinged-roles"] = pinged_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="CenturyTicket", description="Вы успешно удалили `{}` из списка ролей, которые проверяются при создании новых билетов.".format(role.name), color=0x00a8ff)
                await ctx.send(embed=em)
            
            else:
                em = discord.Embed(title="CenturyTicket", description="Эта роль уже не получает пинг при создании новых билетов!", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="CenturyTicket", description="Это недопустимый идентификатор роли. Пожалуйста, повторите попытку с действительным идентификатором роли.")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="CenturyTicket", description="Извините, у вас нет разрешения на выполнение этой команды.", color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
@has_permissions(administrator=True)
async def addadminrole(ctx, role_id=None):

    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        data["verified-roles"].append(role_id)

        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        em = discord.Embed(title="CenturyTicket", description="Вы успешно добавили `{}` в список ролей, которые могут выполнять команды уровня администратора!".format(role.name), color=0x00a8ff)
        await ctx.send(embed=em)

    except:
        em = discord.Embed(title="CenturyTicket", description="Это недопустимый идентификатор роли. Пожалуйста, повторите попытку с действительным идентификатором роли.")
        await ctx.send(embed=em)

@bot.command()
@has_permissions(administrator=True)
async def deladminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        admin_roles = data["verified-roles"]

        if role_id in admin_roles:
            index = admin_roles.index(role_id)

            del admin_roles[index]

            data["verified-roles"] = admin_roles

            with open('data.json', 'w') as f:
                json.dump(data, f)
            
            em = discord.Embed(title="CenturyTicket", description="Вы успешно удалили `{}` из списка ролей, которые проверяются при создании новых билетов.".format(role.name), color=0x00a8ff)

            await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="CenturyTicket", description="Эта роль не получает пинг при создании новых билетов!", color=0x00a8ff)
            await ctx.send(embed=em)

    except:
        em = discord.Embed(title="CenturyTicket", description="Это недопустимый идентификатор роли. Пожалуйста, повторите попытку с действительным идентификатором роли.")
        await ctx.send(embed=em)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.reply(f'Ай ой! Такой команды нет...', delete_after=10)

@bot.event
async def ch_pr():
    await bot.wait_until_ready()
    statuses = [f"github.com/BazZziliuS", f"в тикеты", f"на тебя!"]
    while not bot.is_closed():
        status = random.choice(statuses)
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching,name=status))
        await asyncio.sleep(10)
bot.loop.create_task(ch_pr())

bot.run("TOKEN")
