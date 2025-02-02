import discord 
import os
import random
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Cargar el token desde el archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents para que el bot lea miembros del servidor y contenido de los mensajes
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True  # Habilita el acceso al contenido de los mensajes

bot = commands.Bot(command_prefix="!", intents=intents)

# Cargar cuentas desde un archivo de texto
def cargar_cuentas():
    with open("cuentas.txt", "r") as f:
        return [line.strip() for line in f.readlines()]

def guardar_cuentas(cuentas):
    with open("cuentas.txt", "w") as f:
        for cuenta in cuentas:
            f.write(cuenta + "\n")

# Cargar los usuarios que han invitado a otros
def cargar_invitados():
    if os.path.exists("invitados.txt"):
        with open("invitados.txt", "r") as f:
            return {line.split(':')[0]: int(line.split(':')[1]) for line in f.readlines()}
    return {}

def guardar_invitados(invitados):
    with open("invitados.txt", "w") as f:
        for usuario, cantidad in invitados.items():
            f.write(f"{usuario}:{cantidad}\n")

# Evento para detectar cuando un nuevo usuario se une
@bot.event
async def on_member_join(member):
    guild = member.guild
    invites = await guild.invites()
    invitados = cargar_invitados()

    for invite in invites:
        if invite.uses > 0:
            invocador = invite.inviter.id
            if str(invocador) in invitados:
                invitados[str(invocador)] += 1
            else:
                invitados[str(invocador)] = 1
            guardar_invitados(invitados)
            break

# Comando Articfree con opciones de skins
@bot.command(aliases=["articfree"])
async def Articfree(ctx):
    # Opciones de cuentas disponibles
    opciones = {
        "1": (":flag_es: 1-10 skins / :flag_us: 1-10 skins", 2),  # 2 amigos invitados
        "2": (":flag_es: 10-30 skins / :flag_us: 10-30 skins", 5),  # 5 amigos invitados
        "3": (":flag_es: 30-80 skins / :flag_us: 30-80 skins", 10),  # 10 amigos invitados
        "4": (":flag_es: 100-200 skins / :flag_us: 100-200 skins", 15)  # 15 amigos invitados
    }
    
    # Pedir al usuario que elija un rango
    mensaje = "Selecciona un rango de skins para obtener tu cuenta:\n"
    for key, value in opciones.items():
        mensaje += f"{key}. {value[0]}: :flag_es: Debes invitar a {value[1]} amigos. / :flag_us: You must invite {value[1]} friends.\n"
    mensaje += "\n:flag_es: TIENE QUE SER CON SU PROPIO LINK DE INVITACION NO CON EL OFICIAL / :flag_us: IT MUST BE WITH YOUR OWN INVITATION LINK, NOT THE OFFICIAL ONE"
    await ctx.send(mensaje)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        respuesta = await bot.wait_for("message", check=check, timeout=60.0)
        opcion_seleccionada = respuesta.content.strip()
        
        # Verificar si la opción es válida
        if opcion_seleccionada not in opciones:
            await ctx.send("❌ :flag_es: Opción inválida. Escribe solo el número de la opción. / :flag_us: Invalid option. Type only the option number.")
            return

        nombre_opcion, requisitos = opciones[opcion_seleccionada]

        # Verificar si el usuario ha invitado suficientes amigos
        invitados = cargar_invitados()
        user_id = str(ctx.author.id)
        if user_id in invitados and invitados[user_id] >= requisitos:
            await ctx.send(f"✅ :flag_es: ¡Estás listo para recibir una cuenta de {nombre_opcion}! / :flag_us: You are ready to receive an account of {nombre_opcion}!")
            cuentas = cargar_cuentas()
            if not cuentas:
                await ctx.send("❌ :flag_es: No quedan cuentas disponibles. / :flag_us: No accounts available.")
                return
            cuenta = random.choice(cuentas)
            cuentas.remove(cuenta)
            guardar_cuentas(cuentas)
            await ctx.author.send(f"🎁 Tu cuenta: `{cuenta}`\n:flag_es: No olvides dejar tu review en #reviews o será deshabilitada en 24h. / :flag_us: Don't forget to leave your review in #reviews or it will be disabled in 24h.")
        else:
            await ctx.send(f"❌ :flag_es: No has invitado suficientes amigos para obtener una cuenta de {nombre_opcion}. Invita más amigos. / :flag_us: You haven't invited enough friends to get an account for {nombre_opcion}. Invite more friends.")

    except asyncio.TimeoutError:
        await ctx.send(":flag_es: ⏰ Se agotó el tiempo para seleccionar una opción. / :flag_us: ⏰ Time ran out to select an option.")
    
# Evento cuando el bot esté listo
@bot.event
async def on_ready():
    print(f"✅ {bot.user} está en línea!")

# Ejecutar el bot

from keep_alive import keep_alive

keep_alive()  # Mantiene el bot activo

bot.run(TOKEN)