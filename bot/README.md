# Discord Shop Bot

A Discord bot with a button panel for:
- **🏆 Leaderboard** — top key redeemers
- **🔑 Redeem Key** — redeem a license key via a popup form
- **📦 Check Stock** — see how many keys are in stock per product

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and put your bot token in it:
   ```
   DISCORD_TOKEN=...
   ```
3. Invite the bot to your server with the `bot` and `applications.commands` scopes:
   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_APPLICATION_ID&scope=bot%20applications.commands&permissions=2048
   ```
4. Run the bot:
   ```
   python main.py
   ```

## Usage (admin slash commands)

- `/addproduct name:Fortnite` — add a product
- `/addkeys product:Fortnite keys:KEY-1 KEY-2 KEY-3` — add keys to stock
- `/removeproduct name:Fortnite` — remove a product
- `/panel` — post the button panel in the current channel

Data is stored in `bot/data.json` (created automatically). The panel buttons
are persistent and keep working after the bot restarts.
