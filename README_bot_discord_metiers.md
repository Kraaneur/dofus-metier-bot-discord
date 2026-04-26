# Bot Discord métiers Dofus

## Installation

### 1) Créer un environnement virtuel
Sous Windows (PowerShell) :
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Sous Git Bash :
```bash
py -m venv .venv
source .venv/Scripts/activate
```

### 2) Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3) Définir le token du bot

PowerShell :
```powershell
$env:DISCORD_TOKEN="TON_TOKEN_ICI"
```

Git Bash :
```bash
export DISCORD_TOKEN="TON_TOKEN_ICI"
```

### 4) Lancer le bot
```bash
py bot_discord_metiers.py
```

## Important côté portail Discord
Pour les commandes préfixées `!add`, `!job`, etc., active aussi **Message Content Intent**
dans le portail développeur du bot.

## Commandes
- `!add pseudo métier lvl`
- `!meadd métier lvl`
- `!job métier`
- `!job métier lvlmin`
- `!help`
- `!jobs`

## Exemples
- `!add Arcanin boulanger 100`
- `!meadd paysan 87`
- `!job boulanger`
- `!job boulanger 80`

## Stockage
Les données sont stockées dans `jobs_data.json`.
