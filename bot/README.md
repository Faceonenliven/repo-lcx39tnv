# Discord Shop Bot

A Discord bot, backed by the [NFA Resell API](https://nfa-api.acode.ing/docs),
with a persistent button panel:

- **🏆 Leaderboard** — top key redeemers (tracked locally, ephemeral to the user)
- **🔑 Redeem Key** — opens a form to enter an activation key; on success the bot
  activates it via the API and DMs the account details + loader `.exe`
- **📦 Check Stock** — live stock counts and prices per account type from the API

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in:
   ```
   DISCORD_TOKEN=...      # Discord bot token
   NFA_API_KEY=...        # NFA reseller API key (Panel → API → Create API key)
   ```
3. In the Discord developer portal, make sure the app's **Interactions Endpoint URL**
   is empty (otherwise buttons/commands won't reach the bot over the gateway).
4. Invite the bot with the `bot` and `applications.commands` scopes:
   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_APPLICATION_ID&scope=bot%20applications.commands&permissions=2048
   ```
5. Run the bot:
   ```
   python main.py
   ```

## Slash commands

- `/panel` — post the Leaderboard / Redeem Key panel (admin only)
- `/stock` — post the stock panel with a button per game category

The redemption leaderboard is stored in `bot/data.json` (gitignored). Panel
buttons use fixed `custom_id`s, so they keep working across bot restarts.

## Deploy on Railway

The repo root has a `Procfile`, `requirements.txt`, and `railway.json` so Railway
runs the bot as a worker (`python -u bot/main.py`).

1. On [railway.app](https://railway.app): **New Project → Deploy from GitHub repo**
   and pick this repo.
2. In the service **Variables** tab, add:
   - `DISCORD_TOKEN`
   - `NFA_API_KEY`
3. Deploy. The bot runs 24/7 and restarts automatically on failure.

Note: Railway's filesystem is ephemeral, so `bot/data.json` (the leaderboard)
resets on each redeploy. Attach a Railway **Volume** mounted at `/app/bot` if you
need the leaderboard to persist.
