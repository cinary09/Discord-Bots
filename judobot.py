# main.py
import discord
from discord.ext import commands
import time


TOKEN = "shit dude fuck off to my token u bitch"

PREFIX = "/"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

guild_echo_state = {}  # sunucu bazlı echo açık/kapalı
user_msg_times = {}
MSG_WINDOW = 8
MSG_LIMIT = 5

@bot.event
async def on_ready():
    print(f"Giriş yapıldı: {bot.user} ({bot.user.id})")
    print("Echo bot aktif! Prefix:", PREFIX)

@bot.command(name="help")
async def help_cmd(ctx):
    txt = (
        "**Echo Bot Komutları**\n"
        f"`{PREFIX}echo on`  - Echo aç\n"
        f"`{PREFIX}echo off` - Echo kapat\n"
        f"`{PREFIX}help`     - Yardım menüsü\n\n"
        "Bot kullanıcıların mesajlarını tekrarlar (bot mesajlarını değil).\n"
        "Flood koruması aktif — spam atarsan echo geçici olarak durur."
    )
    await ctx.send(txt)

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    # Joined at can be None in very bizarre cases so just handle that as well
    if member.joined_at is None:
        await ctx.send(f'{member} has no join date.')
    else:
        await ctx.send(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


@bot.command(name="echo")
@commands.has_guild_permissions(manage_guild=True)
async def echo_toggle(ctx, mode: str):
    gid = ctx.guild.id
    mode = mode.lower()
    if mode not in ("on", "off"):
        await ctx.send(f"Kullanım: `{PREFIX}echo on` veya `{PREFIX}echo off`")
        return
    guild_echo_state[gid] = (mode == "on")
    await ctx.send(f"Echo {'aktif' if mode=='on' else 'kapalı'} (sunucu için).")


def is_flood(user_id):
    now = time.time()
    lst = user_msg_times.get(user_id, [])
    lst = [t for t in lst if now - t <= MSG_WINDOW]
    lst.append(now)
    user_msg_times[user_id] = lst
    return len(lst) > MSG_LIMIT

@bot.event
async def on_message(message: discord.Message):
    # Komutları işleyelim
    await bot.process_commands(message)

    # Bot mesajlarını görmezden gel
    if message.author.bot:
        return

    # DM değilse
    if not message.guild:
        return

    gid = message.guild.id

    # Echo açık mı kontrol et
    if not guild_echo_state.get(gid, False):
        return

    # 💡 Komut mesajlarını echo’lama (örnek: /echo on veya /help)
    if message.content.startswith(PREFIX):
        return

    # Flood kontrolü
    if is_flood(message.author.id):
        await message.channel.send(f"{message.author.mention} çok hızlısın 😅 biraz yavaşla!")
        return

    # Normal mesajları echo'la
    text = message.content.strip()
    if text:
        await message.channel.send(f"{message.author.display_name} dedi ki: {text}")

    # Dosyaları da echo'la
    if message.attachments:
        files = [await a.to_file() for a in message.attachments]
        await message.channel.send(f"{message.author.display_name} bir dosya paylaştı:", files=files)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Hata: {error}")
    print("Komut hatası:", error)

bot.run(TOKEN)
