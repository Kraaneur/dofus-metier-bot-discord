import os
import json
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv
import discord
from discord.ext import commands

# =========================
# INIT
# =========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant")

DATA_FILE = Path("jobs_data.json")
MIN_LEVEL = 1
MAX_LEVEL = 100

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# =========================
# MÉTIERS
# =========================
CANONICAL_JOBS = [
    "alchimiste", "bucheron", "chasseur", "mineur", "pecheur", "paysan",
    "bijoutier", "boucher", "boulanger", "bricoleur", "cordonnier",
    "poissonnier", "tailleur",

    "epee", "marteau", "dague", "pelle", "hache", "arc", "baguette", "baton",

    "cordomage", "costumage", "joaillomage",

    "epeefm", "marteaufm", "daguefm", "pellefm", "hachefm",
    "arcfm", "baguettefm", "batonfm",
]

JOB_DISPLAY_NAMES = {
    "alchimiste": "Alchimiste",
    "bucheron": "Bûcheron",
    "chasseur": "Chasseur",
    "mineur": "Mineur",
    "pecheur": "Pêcheur",
    "paysan": "Paysan",
    "bijoutier": "Bijoutier",
    "boucher": "Boucher",
    "boulanger": "Boulanger",
    "bricoleur": "Bricoleur",
    "cordonnier": "Cordonnier",
    "poissonnier": "Poissonnier",
    "tailleur": "Tailleur",

    "epee": "Forgeron d'Épées",
    "marteau": "Forgeron de Marteaux",
    "dague": "Forgeron de Dagues",
    "pelle": "Forgeron de Pelles",
    "hache": "Forgeron de Haches",
    "arc": "Sculpteur d'Arcs",
    "baguette": "Sculpteur de Baguettes",
    "baton": "Sculpteur de Bâtons",

    "cordomage": "Cordomage",
    "costumage": "Costumage",
    "joaillomage": "Joaillomage",

    "epeeFM": "Forgemage d'Épées",
    "marteauFM": "Forgemage de Marteaux",
    "dagueFM": "Forgemage de Dagues",
    "pelleFM": "Forgemage de Pelles",
    "hacheFM": "Forgemage de Haches",
    "arcFM": "Sculptemage d'Arcs",
    "baguetteFM": "Sculptemage de Baguettes",
    "batonFM": "Sculptemage de Bâtons",
}

# =========================
# UTILS
# =========================
def normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text

def resolve_job(job_input: str) -> str | None:
    job = normalize(job_input)
    return job if job in CANONICAL_JOBS else None

# =========================
# DATA
# =========================
def load_data() -> Dict[str, Dict[str, int]]:
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data: Dict[str, Dict[str, int]]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

jobs_data = load_data()

# =========================
# LOG
# =========================
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

# =========================
# COMMANDES
# =========================
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 Aide du bot métiers Dofus",
        description="Voici les commandes disponibles pour gérer les artisans de la guilde.",
        color=0x2ECC71
    )

    embed.add_field(
        name="➕ `!add pseudo métier lvl`",
        value=(
            "Ajoute un artisan à un métier, ou met à jour son niveau s’il existe déjà.\n\n"
            "**Exemples :**\n"
            "`!add Arcanin boulanger 100`\n"
            "`!add Arcanin arc 80`\n"
            "`!add Arcanin marteauFM 75`"
        ),
        inline=False
    )

    embed.add_field(
        name="🗑️ `!delete pseudo [métier]`",
        value=(
            "Supprime un métier ou complètement un artisan.\n\n"
            "**Exemples :**\n"
            "`!delete Arcanin boulanger`\n"
            "`!delete Arcanin`"
        ),
        inline=False
    )

    embed.add_field(
        name="🔎 `!job métier [lvlmin]`",
        value=(
            "Affiche la liste des artisans pour un métier, triés du plus haut niveau au plus bas.\n"
            "Tu peux ajouter un niveau minimum en option.\n\n"
            "**Exemples :**\n"
            "`!job boulanger`\n"
            "`!job arc`\n"
            "`!job marteauFM 70`"
        ),
        inline=False
    )

    embed.add_field(
        name="📜 `!jobs [pseudo]`",
        value=(
            "Sans pseudo, affiche la liste complète des métiers compatibles avec le bot.\n"
            "Avec un pseudo, affiche tous les métiers connus de ce joueur, triés par niveau décroissant.\n\n"
            "**Exemples :**\n"
            "`!jobs`\n"
            "`!jobs Arcanin`"
        ),
        inline=False
    )

    embed.add_field(
        name="ℹ️ `!help`",
        value=(
            "Affiche ce message d’aide.\n\n"
            "**Exemple :**\n"
            "`!help`"
        ),
        inline=False
    )

    

    embed.set_footer(text="Astuce : pour les métiers de mage, ajoute simplement FM à la fin. Exemple : marteauFM")
    await ctx.send(embed=embed)

# -------------------------
# ADD
# -------------------------
@bot.command()
async def add(ctx, pseudo: str, job_input: str, level: int):

    job = resolve_job(job_input)

    if job is None:
        await ctx.send("❌ Métier inconnu.")
        return

    if not (MIN_LEVEL <= level <= MAX_LEVEL):
        await ctx.send("❌ Niveau invalide (1-100).")
        return

    if pseudo not in jobs_data:
        jobs_data[pseudo] = {}

    previous = jobs_data[pseudo].get(job)
    jobs_data[pseudo][job] = level

    save_data(jobs_data)

    display_job = JOB_DISPLAY_NAMES.get(job, job)
    if previous is None:
        await ctx.send(f"✅ `{pseudo}` ajouté en **{display_job} {level}**")
    else:
        await ctx.send(f"🔄 `{pseudo}` mis à jour : **{display_job} {previous} → {level}**")

# -------------------------
# JOB
# -------------------------
@bot.command()
async def job(ctx, job_input: str, lvlmin: int = 1):

    job = resolve_job(job_input)

    if job is None:
        await ctx.send("❌ Métier inconnu.")
        return

    if not (MIN_LEVEL <= lvlmin <= MAX_LEVEL):
        await ctx.send("❌ Niveau minimum invalide.")
        return

    results: List[Tuple[str, int]] = []

    for pseudo, jobs in jobs_data.items():
        lvl = jobs.get(job)
        if lvl and lvl >= lvlmin:
            results.append((pseudo, lvl))

    if not results:
        await ctx.send("Aucun résultat.")
        return

    results.sort(key=lambda x: -x[1])

    display_job = JOB_DISPLAY_NAMES.get(job, job)
    message = f"**{display_job} (lvl ≥ {lvlmin}) :**\n"
    for pseudo, lvl in results:
        message += f"- {pseudo} : {lvl}\n"

    await ctx.send(message[:1900])

# -------------------------
# JOBS
# -------------------------

@bot.command()
async def jobs(ctx, pseudo: str = None):
    # Cas 1 : !jobs
    # Liste tous les métiers compatibles avec le bot
    if pseudo is None:
        message = "**Métiers compatibles avec le bot :**\n\n"

        for bot_name in CANONICAL_JOBS:
            real_name = JOB_DISPLAY_NAMES.get(bot_name, bot_name)
            message += f"- `{bot_name}` : {real_name}\n"

        await ctx.send(message[:1900])
        return

    # Cas 2 : !jobs pseudo
    # Liste tous les métiers d'un joueur
    if pseudo not in jobs_data:
        await ctx.send(f"❌ Aucun métier trouvé pour `{pseudo}`.")
        return

    player_jobs = jobs_data[pseudo]

    if not player_jobs:
        await ctx.send(f"❌ Aucun métier trouvé pour `{pseudo}`.")
        return

    sorted_jobs = sorted(
        player_jobs.items(),
        key=lambda item: item[1],
        reverse=True
    )

    message = f"**Métiers de `{pseudo}` :**\n\n"

    for job, level in sorted_jobs:
        display_job = JOB_DISPLAY_NAMES.get(job, job)
        message += f"- **{display_job}** : niveau **{level}**\n"

    await ctx.send(message[:1900])

# -------------------------
# DELETE
# -------------------------

@bot.command()
async def delete(ctx, pseudo: str, job_input: str = None):

    if pseudo not in jobs_data:
        await ctx.send("❌ Ce pseudo n'existe pas.")
        return

    # Cas 1 : suppression complète
    if job_input is None:
        del jobs_data[pseudo]
        save_data(jobs_data)
        await ctx.send(f"🗑️ `{pseudo}` a été supprimé de la liste.")
        return

    # Cas 2 : suppression d’un métier
    job = resolve_job(job_input)

    if job is None:
        await ctx.send("❌ Métier inconnu.")
        return

    if job not in jobs_data[pseudo]:
        await ctx.send(f"❌ `{pseudo}` n'a pas ce métier.")
        return

    del jobs_data[pseudo][job]

    # Si plus aucun métier → on supprime le joueur
    if not jobs_data[pseudo]:
        del jobs_data[pseudo]
        await ctx.send(f"🗑️ `{pseudo}` supprimé (plus aucun métier).")
    else:
        display_job = JOB_DISPLAY_NAMES.get(job, job)
        await ctx.send(f"🧹 Métier **{display_job}** supprimé pour `{pseudo}`.")

    save_data(jobs_data)

# =========================
# RUN
# =========================
bot.run(TOKEN)