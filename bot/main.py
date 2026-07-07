"""Discord shop bot backed by the NFA Resell API.

Panel buttons: Leaderboard, Redeem Key, Check Stock.
"""

import base64
import io
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import api
import storage

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()

EMBED_COLOR = discord.Color.blurple()

GAME_NAMES = {
    "cs2": "CS2",
    "rust": "Rust",
    "dayz": "DayZ",
    "arc": "Arc Raiders",
    "escape": "Escape",
    "battlefield": "Battlefield",
}


def _pretty_type(account_type: str) -> str:
    """rust_0_250_hours -> '0 250 hours' (game prefix stripped)."""
    parts = account_type.split("_")
    if parts and parts[0] in GAME_NAMES:
        parts = parts[1:]
    return " ".join(parts)


def _account_field(account) -> str:
    """Format the account payload from /activate into a readable block."""
    if not isinstance(account, dict):
        return f"```{str(account)[:1000]}```"
    lines = []
    for label, key in (
        ("Login", "login"),
        ("Account", "account_name"),
        ("Password", "password"),
        ("SteamID64", "steamid64"),
        ("Type", "key_type"),
    ):
        val = account.get(key)
        if val:
            lines.append(f"**{label}:** `{val}`")
    return "\n".join(lines) or "See attached details."


class RedeemModal(discord.ui.Modal, title="Redeem a Key"):
    key = discord.ui.TextInput(
        label="Activation Key",
        placeholder="e.g. 09679151-d1fb-4703-8da3-75680d2e6d1d",
        min_length=8,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            result = await api.activate(self.key.value.strip())
        except api.APIError as e:
            embed = discord.Embed(
                title="Redemption Failed",
                description=f"{e}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        storage.record_redemption(interaction.user.id)

        embed = discord.Embed(
            title="Key Redeemed",
            description=result.get("message") or "Your account is ready.",
            color=discord.Color.green(),
        )
        embed.add_field(name="Account", value=_account_field(result.get("account")), inline=False)

        files = []
        exe_b64 = result.get("exe_base64")
        if exe_b64:
            try:
                raw = base64.b64decode(exe_b64)
                filename = result.get("exe_filename") or "loader.exe"
                files.append(discord.File(io.BytesIO(raw), filename=filename))
                embed.add_field(name="Loader", value=f"Attached: `{filename}`", inline=False)
            except (ValueError, TypeError):
                pass

        await interaction.followup.send(embed=embed, files=files, ephemeral=True)


class ShopPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Leaderboard", style=discord.ButtonStyle.primary, emoji="🏆",
        custom_id="shop_panel:leaderboard",
    )
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        entries = storage.get_leaderboard()
        if not entries:
            desc = "No redemptions yet."
        else:
            medals = ["🥇", "🥈", "🥉"]
            lines = []
            for i, (uid, count) in enumerate(entries):
                rank = medals[i] if i < 3 else f"`#{i + 1}`"
                lines.append(f"{rank} <@{uid}> — **{count}** redemption{'s' if count != 1 else ''}")
            desc = "\n".join(lines)
        embed = discord.Embed(title="🏆 Redemption Leaderboard", description=desc, color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Redeem Key", style=discord.ButtonStyle.success, emoji="🔑",
        custom_id="shop_panel:redeem",
    )
    async def redeem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemModal())


async def _send_category_stock(interaction: discord.Interaction, game_key: str):
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        stock = await api.get_stock()
        prices = await api.get_accounts()
    except api.APIError as e:
        await interaction.followup.send(f"Could not fetch stock: {e}", ephemeral=True)
        return

    game_name = GAME_NAMES.get(game_key, game_key.title())
    lines = []
    for account_type, count in stock.items():
        if account_type.split("_")[0] != game_key:
            continue
        emoji = "🟢" if count > 0 else "🔴"
        price = prices.get(account_type)
        price_str = f" — ${price:.2f}" if price is not None else ""
        lines.append(f"{emoji} {_pretty_type(account_type)} — **{count}** in stock{price_str}")

    embed = discord.Embed(
        title=f"📦 {game_name} Stock",
        description="\n".join(lines) if lines else "No products in this category.",
        color=EMBED_COLOR,
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


class CategoryButton(discord.ui.Button):
    def __init__(self, game_key: str, label: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"stock_cat:{game_key}",
        )
        self.game_key = game_key

    async def callback(self, interaction: discord.Interaction):
        await _send_category_stock(interaction, self.game_key)


class StockPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for game_key, label in GAME_NAMES.items():
            self.add_item(CategoryButton(game_key, label))


class ShopBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(ShopPanel())
        self.add_view(StockPanel())
        await self.tree.sync()


bot = ShopBot()


@bot.tree.command(name="panel", description="Post the shop panel with buttons (admin only)")
@app_commands.default_permissions(administrator=True)
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Shop Panel",
        description=(
            "**🏆 Leaderboard**\nSee the top key redeemers.\n\n"
            "**🔑 Redeem Key**\nRedeem an activation key to claim your account and loader.\n\n"
            "Use `/stock` for live stock by category."
        ),
        color=EMBED_COLOR,
    )
    await interaction.response.send_message(embed=embed, view=ShopPanel())


@bot.tree.command(name="stock", description="Post the stock panel with category buttons")
async def stock(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📦 Stock",
        description="Click a category below to see the stock for all its products.",
        color=EMBED_COLOR,
    )
    await interaction.response.send_message(embed=embed, view=StockPanel())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


if __name__ == "__main__":
    bot.run(TOKEN)
