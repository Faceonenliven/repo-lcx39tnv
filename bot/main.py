"""Discord shop bot backed by the NFA Resell API.

Panel buttons: Leaderboard, Redeem Key, Check Stock.
"""

import base64
import io
import os
import re

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


def _human_duration(seconds: float) -> str:
    seconds = int(max(0, seconds))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if not parts:
        parts.append(f"{s}s")
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


async def _coin_unavailable(interaction: discord.Interaction) -> bool:
    if api.coin_api_configured():
        return False
    msg = "The coin bot isn't linked yet (an admin must set `COIN_API_BASE` and `COIN_API_KEY`)."
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)
    return True


async def _send_leaderboard(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    medals = ["🥇", "🥈", "🥉"]

    if api.coin_api_configured():
        try:
            entries = await api.coin_leaderboard()
        except api.APIError as e:
            await interaction.followup.send(f"Could not fetch leaderboard: {e}", ephemeral=True)
            return
        title = "🏆 Coin Leaderboard"
        unit = "coin"
    else:
        entries = storage.get_leaderboard()
        title = "🏆 Redemption Leaderboard"
        unit = "redemption"

    if not entries:
        desc = "No entries yet."
    else:
        lines = []
        for i, (uid, amount) in enumerate(entries):
            rank = medals[i] if i < 3 else f"`#{i + 1}`"
            lines.append(f"{rank} <@{uid}> — **{amount}** {unit}{'s' if amount != 1 else ''}")
        desc = "\n".join(lines)

    embed = discord.Embed(title=title, description=desc, color=EMBED_COLOR)
    await interaction.followup.send(embed=embed, ephemeral=True)


class PayModal(discord.ui.Modal, title="Pay Coins"):
    recipient = discord.ui.TextInput(
        label="Recipient (@mention or user ID)",
        placeholder="@someone or 123456789012345678",
        max_length=50,
    )
    amount = discord.ui.TextInput(label="Amount", placeholder="e.g. 5", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        match = re.search(r"\d{15,20}", self.recipient.value)
        if not match:
            await interaction.followup.send("Couldn't read that recipient — use an @mention or user ID.", ephemeral=True)
            return
        to_id = int(match.group())
        try:
            amount = int(self.amount.value.strip())
        except ValueError:
            amount = 0
        if amount <= 0:
            await interaction.followup.send("Amount must be a positive number.", ephemeral=True)
            return
        if to_id == interaction.user.id:
            await interaction.followup.send("You can't pay yourself.", ephemeral=True)
            return
        try:
            result = await api.coin_pay(interaction.user.id, to_id, amount)
        except api.APIError as e:
            await interaction.followup.send(f"Payment failed: {e}", ephemeral=True)
            return
        await interaction.followup.send(
            f"💸 Sent **{amount}** coin{'s' if amount != 1 else ''} to <@{to_id}>! "
            f"Your balance: **{result.get('from_coins', '?')}**",
            ephemeral=True,
        )
        if interaction.channel is not None:
            try:
                await interaction.channel.send(
                    f"💸 {interaction.user.mention} sent **{amount}** coin{'s' if amount != 1 else ''} to <@{to_id}>!"
                )
            except discord.HTTPException:
                pass


class ReplaceModal(discord.ui.Modal, title="Replace an Invalid Key"):
    key = discord.ui.TextInput(
        label="Activation Key",
        placeholder="e.g. 09679151-d1fb-4703-8da3-75680d2e6d1d",
        min_length=8,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            data = await api.check_account(self.key.value.strip())
        except api.APIError as e:
            await interaction.followup.send(f"Replacement check failed: {e}", ephemeral=True)
            return
        result = data.get("result")
        if result == "valid":
            await interaction.followup.send("✅ That account is still **valid** — no replacement needed.", ephemeral=True)
        elif result == "replaced":
            replacement = data.get("replacement_key")
            body = "🔄 Your account was **replaced** under the 3-hour warranty.\n\n"
            if replacement:
                body += f"**New key:** ||`{replacement}`||\n\nRedeem it with the 🔑 Redeem Key button — keep it private."
            else:
                body += "Check the panel for your new replacement key."
            await interaction.followup.send(body, ephemeral=True)
        else:
            note = data.get("message") or "the account is still valid or outside the 3-hour warranty window"
            await interaction.followup.send(
                f"❌ No replacement issued — {note}. If you think this is a mistake, contact support.",
                ephemeral=True,
            )


class CoinPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Balance", style=discord.ButtonStyle.primary, emoji="💰",
        custom_id="coin_panel:balance",
    )
    async def balance(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await _coin_unavailable(interaction):
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            p = await api.coin_profile(interaction.user.id)
        except api.APIError as e:
            await interaction.followup.send(f"Could not fetch balance: {e}", ephemeral=True)
            return
        embed = discord.Embed(title=f"💰 {interaction.user.display_name}'s Balance", color=EMBED_COLOR)
        embed.add_field(name="Coins", value=f"**{p.get('coins', 0)}**", inline=True)
        embed.add_field(name="Rewards earned", value=str(p.get("rewards_count", 0)), inline=True)
        embed.add_field(name="Total online time", value=_human_duration(p.get("total_seconds", 0)), inline=False)
        embed.add_field(
            name="Next coin in",
            value=f"{_human_duration(p.get('remaining_seconds', 0))}  ({p.get('percent', 0):.1f}% there)",
            inline=False,
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Check Status", style=discord.ButtonStyle.secondary, emoji="✅",
        custom_id="coin_panel:check",
    )
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await _coin_unavailable(interaction):
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            c = await api.coin_check(interaction.user.id)
        except api.APIError as e:
            await interaction.followup.send(f"Could not run the check: {e}", ephemeral=True)
            return
        if not c.get("found"):
            await interaction.followup.send(
                "I couldn't see you in the coin bot's server — make sure you're in the server it tracks.",
                ephemeral=True,
            )
            return
        eligible = c.get("eligible", False)
        embed = discord.Embed(
            title=f"Eligibility Check — {interaction.user.display_name}",
            color=discord.Color.green() if eligible else discord.Color.red(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(
            name="Online status",
            value=f"{'✅' if c.get('status_ok') else '❌'} `{c.get('status')}` "
            f"(need one of: {c.get('eligible_statuses')})",
            inline=False,
        )
        embed.add_field(
            name="Required status text",
            value=f"{'✅' if c.get('text_ok') else '❌'} must contain: `{c.get('required_status')}`\n"
            f"status shown: `{c.get('status_text') or '(none set)'}`",
            inline=False,
        )
        embed.add_field(
            name="Currently earning?",
            value="✅ **Yes** — keep it up!" if eligible else "❌ **No** — fix the above",
            inline=False,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Leaderboard", style=discord.ButtonStyle.secondary, emoji="🏆",
        custom_id="coin_panel:leaderboard",
    )
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_leaderboard(interaction)

    @discord.ui.button(
        label="Pay", style=discord.ButtonStyle.success, emoji="💸",
        custom_id="coin_panel:pay",
    )
    async def pay(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await _coin_unavailable(interaction):
            return
        await interaction.response.send_modal(PayModal())

    @discord.ui.button(
        label="How It Works", style=discord.ButtonStyle.secondary, emoji="❓",
        custom_id="coin_panel:how",
    )
    async def howitworks(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await _coin_unavailable(interaction):
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            s = await api.coin_settings()
        except api.APIError as e:
            await interaction.followup.send(f"Could not fetch settings: {e}", ephemeral=True)
            return
        coin_name = s.get("coin_name", "coin")
        embed = discord.Embed(
            title="How to Earn Coins",
            color=EMBED_COLOR,
            description=(
                f"**1.** Set your Discord **custom status** to include:\n"
                f"> `{s.get('required_status')}`\n\n"
                f"**2.** Stay **{s.get('eligible_statuses')}** (i.e. actually online).\n\n"
                f"**3.** For every **{s.get('reward_hours', 0):g} hours** of online time *with the status*, "
                f"you earn **{s.get('coins_per_reward')} {coin_name}(s)**.\n\n"
                f"Only time while you're online **and** showing the status counts. "
                f"Use ✅ **Check Status** to confirm you're set up, and 💰 **Balance** to track progress."
            ),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Replace Key", style=discord.ButtonStyle.danger, emoji="♻️",
        custom_id="coin_panel:replace",
    )
    async def replace(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReplaceModal())


class ShopPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Leaderboard", style=discord.ButtonStyle.primary, emoji="🏆",
        custom_id="shop_panel:leaderboard",
    )
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _send_leaderboard(interaction)

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
        display = "5+" if count > 5 else str(count)
        price = prices.get(account_type)
        price_str = f" — ${price:.2f}" if price is not None else ""
        lines.append(f"{emoji} {_pretty_type(account_type)} — **{display}** in stock{price_str}")

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
        self.add_view(CoinPanel())
        self.tree.add_command(CoinAdminGroup())
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


@bot.tree.command(name="coins", description="Post the coin panel with buttons (admin only)")
@app_commands.default_permissions(administrator=True)
async def coins(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🪙 Coin Panel",
        description=(
            "**💰 Balance** — your coins and progress to the next one\n"
            "**✅ Check Status** — see if you're currently earning\n"
            "**🏆 Leaderboard** — top coin holders\n"
            "**💸 Pay** — send coins to another member\n"
            "**❓ How It Works** — how to earn coins\n"
            "**♻️ Replace Key** — replace an invalid key (3-hour warranty)"
        ),
        color=EMBED_COLOR,
    )
    await interaction.response.send_message(embed=embed, view=CoinPanel())


@app_commands.guild_only()
@app_commands.default_permissions(manage_guild=True)
class CoinAdminGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="coinadmin", description="Coin bot administration")

    async def _run(self, interaction: discord.Interaction, coro, fmt):
        if await _coin_unavailable(interaction):
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            result = await coro
        except api.APIError as e:
            await interaction.followup.send(f"Failed: {e}", ephemeral=True)
            return
        await interaction.followup.send(fmt(result), ephemeral=True)

    @app_commands.command(name="addcoins", description="Add (or subtract) a user's coins")
    @app_commands.describe(user="Member", amount="Amount (negative to remove)")
    async def addcoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
        await self._run(
            interaction, api.coin_adjust(user.id, amount),
            lambda r: f"{user.mention} now has **{r.get('coins')}** coin(s).",
        )

    @app_commands.command(name="removecoins", description="Remove coins from a user")
    @app_commands.describe(user="Member", amount="How many to remove")
    async def removecoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
        await self._run(
            interaction, api.coin_adjust(user.id, -abs(amount)),
            lambda r: f"{user.mention} now has **{r.get('coins')}** coin(s).",
        )

    @app_commands.command(name="setcoins", description="Set a user's coin balance")
    async def setcoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
        await self._run(
            interaction, api.coin_set(user.id, amount),
            lambda r: f"Set {user.mention} to **{r.get('coins')}** coin(s).",
        )

    @app_commands.command(name="setrequiredstatus", description="Set the required custom-status text")
    async def setrequiredstatus(self, interaction: discord.Interaction, text: str):
        await self._run(
            interaction, api.coin_update_setting("required_status", text),
            lambda r: f"Required status updated to:\n> `{text}`",
        )

    @app_commands.command(name="setrewardhours", description="Hours of online time per coin reward")
    async def setrewardhours(self, interaction: discord.Interaction, hours: float):
        await self._run(
            interaction, api.coin_update_setting("reward_hours", hours),
            lambda r: f"Reward interval set to **{hours:g} hours**.",
        )

    @app_commands.command(name="setcoinsperreward", description="Coins granted each interval")
    async def setcoinsperreward(self, interaction: discord.Interaction, amount: int):
        await self._run(
            interaction, api.coin_update_setting("coins_per_reward", max(1, amount)),
            lambda r: f"Coins per reward set to **{max(1, amount)}**.",
        )

    @app_commands.command(name="seteligiblestatuses", description="e.g. 'online,dnd'")
    async def seteligiblestatuses(self, interaction: discord.Interaction, statuses: str):
        await self._run(
            interaction, api.coin_update_setting("eligible_statuses", statuses),
            lambda r: f"Eligible statuses set to: `{r.get('settings', {}).get('eligible_statuses', statuses)}`",
        )

    @app_commands.command(name="settings", description="Show the coin bot's current settings")
    async def settings(self, interaction: discord.Interaction):
        def fmt(s):
            return (
                f"**Required status:** `{s.get('required_status')}`\n"
                f"**Reward interval:** {s.get('reward_hours', 0):g} hours\n"
                f"**Coins per reward:** {s.get('coins_per_reward')}\n"
                f"**Eligible statuses:** `{s.get('eligible_statuses')}`"
            )
        await self._run(interaction, api.coin_settings(), fmt)


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
