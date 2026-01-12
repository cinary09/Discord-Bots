# Atık Ayırma Botu ♻️
import discord
from discord.ext import commands
import json
import os
import difflib

# 🔧 AYARLAR
TOKEN = "IF U READ THIS UR ................................... are bitch u litte fella"
DATA_FILE = "waste_db.json"
PREFIX = "/"
INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS, help_command=None)

# 📦 Varsayılan veritabanı
DEFAULT_DB = {
    "plastik şişe": {
        "category": "Geri dönüşüm",
        "note": "Kapağını çıkar, hafifçe durula, sıkıştırıp geri dönüşüm kutusuna at.",
        "emoji": "♻️"
    },
    "cam şişe": {
        "category": "Geri dönüşüm",
        "note": "Kırık cam dikkat! Kırıksa özel kutu/geri dönüşüm merkezine.",
        "emoji": "♻️"
    },
    "kağıt": {
        "category": "Geri dönüşüm",
        "note": "Temiz kağıtları geri dönüşüme at. Islak veya yağlıysa çöpe.",
        "emoji": "📄"
    },
    "pil": {
        "category": "Tehlikeli atık",
        "note": "Pil ve aküler özel toplama noktalarına verilmeli.",
        "emoji": "⚠️"
    },
    "organik atık": {
        "category": "Kompost",
        "note": "Yemek artıkları, meyve kabukları (et/yağlılar hariç) komposta uygundur.",
        "emoji": "🌱"
    }
}

# 🧠 Fonksiyonlar
def load_db(path=DATA_FILE):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DB, f, ensure_ascii=False, indent=2)
        return DEFAULT_DB.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db, path=DATA_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def find_best_match(query, db_keys, cutoff=0.6):
    query_low = query.lower()
    matches = difflib.get_close_matches(query_low, db_keys, n=3, cutoff=cutoff)
    substring_matches = [k for k in db_keys if query_low in k]
    result = substring_matches + [m for m in matches if m not in substring_matches]
    return result

def embed_for_item(name, info):
    embed = discord.Embed(title=name.title(), description=info.get("note", ""), color=0x2ecc71)
    embed.add_field(name="Kategori", value=info.get("category", "Bilinmiyor"), inline=True)
    emoji = info.get("emoji", "")
    if emoji:
        embed.set_author(name=f"{emoji} Atık Ayır Bot")
    return embed

# 📂 Veritabanını yükle
waste_db = load_db()

# 🟢 BOT OLAYLARI
@bot.event
async def on_ready():
    print(f"Bot aktif oldu: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Atıkları ayır | !yardım"))

# 🧾 Komutlar
@bot.command(name="yardım")
async def yardım(ctx):
    msg = (
        "**Atık Ayır Botu ♻️**\n\n"
        "Komutlar:\n"
        "`!ayır <eşya>` → Eşyanın nereye gideceğini söyler.\n"
        "`!liste <kelime>` → Benzer öğeleri gösterir.\n"
        "`!ekle <eşya> | <kategori> | <not>` → (Sahip) Yeni öğe ekler.\n"
        "`!kaydet` → Veritabanını kaydeder.\n\n"
        "Örnek: `!ayır plastik şişe`\n"
    )
    await ctx.send(msg)

@bot.command(name="ayır")
async def ayir(ctx, *, item: str):
    item_low = item.lower().strip()
    keys = list(waste_db.keys())

    # Tam eşleşme
    if item_low in waste_db:
        info = waste_db[item_low]
        await ctx.send(embed=embed_for_item(item_low, info))
        return

    # Yakın eşleşme
    matches = find_best_match(item_low, keys, cutoff=0.55)
    if matches:
        best = matches[0]
        info = waste_db[best]
        e = embed_for_item(best, info)
        e.set_footer(text=f"Benim tahminim: '{best}'. Eğer farklıysa `!liste {item}` yaz.")
        await ctx.send(embed=e)
        return

    await ctx.send(
        f"'{item}' için kesin bilgi bulamadım 😅\n"
        "Genel ipucu: cam/metal/plastik = **geri dönüşüm**, pil/yağ = **tehlikeli atık**."
    )

@bot.command(name="liste")
async def liste(ctx, *, query: str):
    keys = list(waste_db.keys())
    matches = find_best_match(query.lower(), keys, cutoff=0.4)
    if not matches:
        await ctx.send("Benzer öğe bulunamadı 😕")
        return
    out = "\n".join(f"- {m}" for m in matches[:10])
    await ctx.send(f"Benzer öğeler:\n{out}")

@bot.command(name="ekle")
@commands.is_owner()
async def ekle(ctx, *, payload: str):
    parts = [p.strip() for p in payload.split("|")]
    if len(parts) < 2:
        await ctx.send("Format: `!ekle eşya | kategori | kısa not`")
        return
    name = parts[0].lower()
    category = parts[1]
    note = parts[2] if len(parts) >= 3 else ""
    waste_db[name] = {"category": category, "note": note, "emoji": "♻️"}
    save_db(waste_db)
    await ctx.send(f"`{name}` eklendi ✅ ({category})")

@bot.command(name="kaydet")
@commands.is_owner()
async def kaydet(ctx):
    save_db(waste_db)
    await ctx.send("Veritabanı kaydedildi 💾")

# ⚠️ Hata yakalama
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Bu komut sadece bot sahibine açık 🚫")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Eksik argüman! `!yardım` yaz bak 😉")
    else:
        await ctx.send(f"Bir hata oluştu: `{str(error)}`")

# 🚀 Botu çalıştır
if __name__ == "__main__":
    bot.run(TOKEN)
