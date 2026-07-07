"""Discord shop bot with a button panel for leaderboard, key redemption, and stock."""

import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import storage

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()

EMBED_COLOR = discord.Color.blurple()


class RedeemModal(discord.ui.Modal, title="Redeem a Key"):
    key = discord.ui.TextInput(
        label="License Key",
        placeholder="Enter your key here...",
        min_length=1,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        product = storage.redeem_key(self.key.value.strip(), interaction.user.id)
        if product:
            embed = discord.Embed(
                title="Key Redeemed",
                description=f"Your key for **{product}** has been redeemed successfully!",
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title="Invalid Key",
                description="That key is invalid or has already been redeemed.",
                color=discord.Color.red(),
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


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

    @discord.ui.button(
        label="Check Stock", style=discord.ButtonStyle.secondary, emoji="📦",
        custom_id="shop_panel:stock",
    )
    async def stock(self, interaction: discord.Interaction, button: discord.ui.Button):
        stock = storage.get_stock()
        if not stock:
            desc = "No products configured yet."
        else:
            lines = []
            for name, count in stock.items():
                status = "🟢" if count > 0 else "🔴"
                lines.append(f"{status} **{name}** — {count} key{'s' if count != 1 else ''} in stock")
            desc = "\n".join(lines)
        embed = discord.Embed(title="📦 Current Stock", description=desc, color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ShopBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(ShopPanel())
        await self.tree.sync()


bot = ShopBot()


@bot.tree.command(name="panel", description="Post the shop panel with buttons (admin only)")
@app_commands.default_permissions(administrator=True)
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Shop Panel",
        description=(
            "**🏆 Leaderboard**\nSee the top key redeemers.\n\n"
            "**🔑 Redeem Key**\nRedeem a license key you purchased.\n\n"
            "**📦 Check Stock**\nView current key stock for each product."
        ),
        color=EMBED_COLOR,
    )
    await interaction.channel.send(embed=embed, view=ShopPanel())
    await interaction.response.send_message("Panel posted.", ephemeral=True)


@bot.tree.command(name="addproduct", description="Add a new product (admin only)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(name="Product name, e.g. Fortnite")
async def addproduct(interaction: discord.Interaction, name: str):
    if storage.add_product(name):
        msg = f"Product **{name}** added."
    else:
        msg = f"Product **{name}** already exists."
    await interaction.response.send_message(msg, ephemeral=True)


@bot.tree.command(name="removeproduct", description="Remove a product (admin only)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(name="Product name to remove")
async def removeproduct(interaction: discord.Interaction, name: str):
    if storage.remove_product(name):
        msg = f"Product **{name}** removed."
    else:
        msg = f"No product named **{name}** found."
    await interaction.response.send_message(msg, ephemeral=True)


@bot.tree.command(name="addkeys", description="Add license keys to a product's stock (admin only)")
@app_commands.default_permissions(administrator=True)
@app_commands.describe(product="Product name", keys="One or more keys, separated by spaces or commas")
async def addkeys(interaction: discord.Interaction, product: str, keys: str):
    key_list = [k.strip() for k in keys.replace(",", " ").split() if k.strip()]
    added = storage.add_keys(product, key_list)
    if added == -1:
        msg = f"No product named **{product}** found. Add it first with `/addproduct`."
    else:
        msg = f"Added **{added}** key{'s' if added != 1 else ''} to **{product}**."
    await interaction.response.send_message(msg, ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


if __name__ == "__main__":
    bot.run(TOKEN)
