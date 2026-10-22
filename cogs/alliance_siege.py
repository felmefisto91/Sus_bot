import asyncio
import datetime
import logging
from typing import Dict, List, Tuple

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from services.localization import get_lang, t
from services.sheets import sheets_service, get_current_week_start_date
from services.db import db_manager

logger = logging.getLogger("AllianceSiegeBot.AllianceSiege")

# Fixed mapping of System -> Region
SYSTEM_REGION_MAP = {
    "K212-A": "Scalding Pass",
    "SG-75T": "Scalding Pass",
    "K7-LDX": "Scalding Pass",
    "U-IVGH": "Scalding Pass",
    "HD-AJ7": "Wicked Creek",
    "SJJ-4F": "Wicked Creek",
    "OAIG-0": "Wicked Creek",
    "C0O6-K": "Wicked Creek",
    "SR-4EK": "Wicked Creek",
    "OEG-K9": "Detorid",
    "PQRE-W": "Detorid",
    "5DE-QS": "Wicked Creek",
    "4-43BW": "Scalding Pass",
    "8CN-CH": "Scalding Pass",
    "LBC-AW": "Scalding Pass",
    "B-5UFY": "Detorid",
    "L-Z9KJ": "Wicked Creek",
    "V-F6DQ": "Scalding Pass",
    "74L2-U": "Insmother",
    "D-P1EH": "Insmother",
    "WU-FHQ": "Detorid",
    "BTLH-I": "Cache",
    "0LY-W1": "Cache",
    "6OU9-U": "Detorid",
    "3S-6VU": "Scalding Pass",
    "B-WQDP": "Wicked Creek",
    "X2-ZA5": "Scalding Pass",
    "0-6VZ5": "Insmother",
    "RERZ-L": "Insmother",
    "8OYE-Z": "Cache",
    "K85Y-6": "Cache",
    "LQ-01M": "Cache",
    "NG-M8K": "Cache",
    "PKN-NJ": "Cache",
    "RV5-TT": "Cache",
    "3Q-VZA": "Wicked Creek",
    "4-CM8I": "Scalding Pass",
    "Q4C-S5": "Scalding Pass",
    "GGE-5Q": "Wicked Creek",
    "5E-CMA": "Wicked Creek",
    "5J4K-9": "Detorid",
    "MD-0AW": "Detorid",
    "0UBC-R": "Insmother",
    "LQ-OAI": "Scalding Pass",
    "UM-SCG": "Wicked Creek",
    "88A-RA": "Insmother",
    "6-EQYE": "Scalding Pass",
    "1-7HVI": "Scalding Pass",
    "GPLB-C": "Wicked Creek",
    "78-0R6": "Insmother",
    "5-MQQ7": "Scalding Pass",
    "GDHN-K": "Insmother",
    "M9-MLR": "Scalding Pass",
    "XV-MWG": "Scalding Pass",
    "CR2-PQ": "Insmother",
    "H-FGJO": "Detorid",
    "A-4JOO": "Wicked Creek",
    "G9NE-B": "Wicked Creek",
    "B-1UJC": "Scalding Pass",
    "Q-NA5H": "Scalding Pass",
    "1QZ-Y9": "Scalding Pass",
    "ZDB-HT": "Scalding Pass",
    "M3-KAQ": "Wicked Creek",
    "U104-3": "Wicked Creek",
    "RYC-19": "Scalding Pass",
    "WO-GC0": "Scalding Pass",
    "GB-6X5": "Insmother",
    "7EX-14": "Insmother",
    "5C-RPA": "Insmother",
    "K-RMI5": "Cache",
    "HPBE-D": "Wicked Creek",
    "M-MBRT": "Wicked Creek",
    "R4N-LD": "Wicked Creek",
    "TP7-KE": "Wicked Creek",
    "5Q65-4": "Wicked Creek",
    "R0-DMM": "Wicked Creek",
    "DUO-51": "Wicked Creek",
    "Z-A8FS": "Wicked Creek",
    "E5T-CS": "Cache",
    "V-4DBR": "Detorid",
    "SK42-F": "Detorid",
    "EU9-J3": "Detorid",
    "5F-MG1": "Cache",
    "W4C8-Q": "Cache",
    "2-KPW6": "Scalding Pass",
    "5NQI-E": "Wicked Creek",
    "7K-NSE": "Wicked Creek",
    "JEQG-7": "Wicked Creek",
    "OR-7N5": "Wicked Creek",
    "IAK-JW": "Scalding Pass",
    "KZFV-4": "Scalding Pass",
    "5M2-KP": "Insmother",
    "KDG-TA": "Insmother",
    "27-HP0": "Insmother",
    "RZ-TI6": "Insmother",
    "B-II34": "Insmother",
    "DFH-V5": "Insmother",
    "EJ48-O": "Insmother",
    "ROJ-B0": "Insmother",
    "1TG7-W": "Insmother",
    "A-TJ0G": "Insmother",
    "QYD-WK": "Insmother",
    "R959-U": "Insmother",
    "U-UTU9": "Insmother",
    "9N-0HF": "Detorid",
    "4NDT-W": "Detorid",
    "9-OUGJ": "Detorid",
    "U-OVFR": "Detorid",
    "2-Q4YG": "Insmother",
    "MSG-BZ": "Insmother",
    "4DS-OI": "Insmother",
    "7L3-JS": "Insmother",
    "8EF-58": "Insmother",
    "C8H5-X": "Insmother",
    "O-7LAI": "Insmother",
    "TZN-2V": "Insmother",
    "WF4C-8": "Insmother",
    "3-0FYP": "Insmother",
    "UZ-QXW": "Wicked Creek",
    "O-5TN1": "Cache",
    "TPG-DD": "Cache",
    "R-3FBU": "Scalding Pass",
    "ARG-3R": "Scalding Pass",
    "EIN-QG": "Scalding Pass",
    "JMH-PT": "Scalding Pass",
    "C-LTXS": "Wicked Creek",
    "DE-A7P": "Scalding Pass",
    "X9V-15": "Scalding Pass",
    "0RI-OV": "Wicked Creek",
    "JZ-B5Y": "Cache",
    "NIF-JE": "Cache",
    "WV0D-1": "Scalding Pass",
    "8-OZU1": "Wicked Creek",
    "G9L-LP": "Wicked Creek",
    "MLQ-O9": "Wicked Creek",
    "X-ARMF": "Wicked Creek",
    "KD-KPR": "Insmother",
    "KS-1TS": "Insmother",
    "RD-FWY": "Insmother",
    "VBPT-T": "Insmother",
    "ZO-4AR": "Insmother",
    "I6-SYN": "Cache",
    "VK-A5G": "Cache",
    "LMM7-L": "Cache",
    "2-2EWC": "Cache",
    "E1W-TB": "Cache",
    "04EI-U": "Cache",
    "BLMX-B": "Cache",
    "Q-UEN6": "Cache",
    "M-MCP8": "Cache",
    "5-2PQU": "Insmother",
    "M4-GJ6": "Insmother",
    "SN9-3Z": "Insmother",
    "38NZ-1": "Insmother",
    "HL-VZX": "Insmother",
    "W-MF6J": "Insmother",
    "4LB-EL": "Insmother",
    "3AE-CP": "Insmother",
    "9OLQ-6": "Insmother",
    "MOCW-2": "Insmother",
    "Q-3HS5": "Insmother",
    "GK5Z-T": "Insmother",
    "0TYR-T": "Wicked Creek",
    "L-FM3P": "Wicked Creek",
    "8-VC6H": "Cache",
    "N7-KGJ": "Insmother",
    "VD-8QY": "Insmother",
    "3U-48K": "Insmother",
    "G-EURJ": "Insmother",
    "X5-0EM": "Insmother",
    "E-JCUS": "Wicked Creek",
    "LP1M-Q": "Wicked Creek",
    "GPD5-0": "Wicked Creek",
    "EKPB-3": "Insmother",
    "04-EHC": "Insmother",
    "C1G-XC": "Insmother",
    "5IH-GL": "Insmother",
    "IVP-KA": "Cache",
    "M-CNUD": "Cache",
    "W2T-TR": "Cache",
    "EUU-4N": "Insmother",
    "GM-50Y": "Wicked Creek",
    "F39H-1": "Insmother",
    "W-6GBI": "Insmother",
    "XKH-6O": "Insmother",
    "XQP-9C": "Insmother",
    "J-ZYSZ": "Insmother",
    "AGCP-I": "Insmother",
    "FX4L-2": "Insmother",
    "PT-21C": "Insmother",
    "TK-DLH": "Insmother",
    "Z182-R": "Insmother",
    "MJ-LGH": "Insmother",
    "4M-QXK": "Insmother",
    "8-WYQZ": "Insmother",
    "8G-2FP": "Insmother",
    "O-9G5Y": "Insmother",
    "X1-IZ0": "Insmother",
    "1KAW-T": "Detorid",
    "03-OR2": "Scalding Pass",
    "8-SPNN": "Cache",
    "B-T6BT": "Cache",
    "U-QMOA": "Cache",
    "8-BIE3": "Cache",
    "4S0-NP": "Cache",
    "GR-X26": "Detorid",
    "Q-K2T7": "Scalding Pass",
    "U93O-A": "Cache",
    "J7-BDX": "Wicked Creek",
    "30-YOU": "Wicked Creek",
    "384-IN": "Wicked Creek",
    "4F89-U": "Wicked Creek",
    "MKIG-5": "Wicked Creek",
    "YHEN-G": "Wicked Creek",
    "6-L4YC": "Wicked Creek",
    "UDE-FX": "Insmother",
    "4YO-QK": "Cache",
    "0-VG7A": "Insmother",
    "F-3FOY": "Wicked Creek",
    "P-N5N9": "Scalding Pass",
    "D-6H64": "Cache",
    "SHBF-V": "Insmother",
    "U2-28D": "Scalding Pass",
    "A-80UA": "Scalding Pass",
    "LJ-RJK": "Cache",
    "I-2705": "Cache",
    "C-6YHJ": "Cache",
    "YE1-9S": "Cache",
    "G063-U": "Wicked Creek",
    "W-QN5X": "Wicked Creek",
    "07-SLO": "Wicked Creek",
    "GRHS-B": "Wicked Creek",
    "J-RXYN": "Wicked Creek",
    "OAQY-M": "Scalding Pass",
    "OX-S7P": "Scalding Pass",
    "4CJ-AC": "Insmother",
    "67Y-NR": "Insmother",
    "A24L-V": "Insmother",
    "QTME-D": "Insmother",
    "RQN-OO": "Insmother",
    "L5-UWT": "Insmother",
    "YPW-M4": "Insmother",
    "74-VZA": "Insmother",
    "EFM-C4": "Insmother",
    "I-1QKL": "Insmother",
    "Q7-FZ8": "Insmother",
    "F3-8X2": "Insmother",
    "FN0-QS": "Insmother",
    "X0-6LH": "Insmother",
    "2JT-3Q": "Insmother",
    "7-JT09": "Insmother",
    "I3CR-F": "Insmother",
    "S0U-MO": "Insmother",
    "V-QXXK": "Insmother",
    "HZ-O18": "Insmother",
    "N-O53U": "Insmother",
    "LVL-GZ": "Insmother",
    "TTP-2B": "Insmother",
    "1ZF-PJ": "Insmother",
    "HFC-AQ": "Insmother",
}

ROSTER_HEADERS = ["Member / Corp", "System", "Region"]
PROGRESS_HEADERS = ["Week Date", "Member / Corp", "System", "Status", "Cleared By", "Cleared At"]

DEFAULT_ROSTER_SAMPLE = [
    ("UAN", s, r) for s, r in SYSTEM_REGION_MAP.items()
]

def get_roster_sheet():
    sheet = sheets_service.get_worksheet(config.ALLIANCE_ROSTER_SHEET, default_headers=ROSTER_HEADERS)
    if len(sheet.get_all_values()) <= 1:
        for corp, system, region in DEFAULT_ROSTER_SAMPLE:
            sheet.append_row([corp, system, region])
    return sheet

def get_progress_sheet():
    return sheets_service.get_progress_worksheet(default_headers=PROGRESS_HEADERS)

def fetch_alliance_data(force_refresh: bool = False):
    if force_refresh:
        logger.info("Force refresh requested: updating local cache from Google Sheets...")
    week_date = get_current_week_start_date()
    roster = db_manager.get_roster()
    progress = db_manager.get_progress(week_date)
    return roster, progress

async def corp_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    roster, _ = await asyncio.to_thread(fetch_alliance_data)
    corps = sorted(roster.keys())
    return [
        app_commands.Choice(name=corp, value=corp)
        for corp in corps if current.lower() in corp.lower()
    ][:25]

async def region_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    regions = sorted(list(set(SYSTEM_REGION_MAP.values())))
    return [
        app_commands.Choice(name=region, value=region)
        for region in regions if current.lower() in region.lower()
    ][:25]

async def system_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    # Get the selected region from the interaction namespace
    namespace = interaction.namespace
    region = namespace.region if namespace else None

    if not region:
        # If no region is selected, show all systems or a limited set
        return [
            app_commands.Choice(name=system, value=system)
            for system in SYSTEM_REGION_MAP.keys() if current.lower() in system.lower()
        ][:25]

    # Filter systems by the selected region
    return [
        app_commands.Choice(name=system, value=system)
        for system, r in SYSTEM_REGION_MAP.items()
        if r == region and current.lower() in system.lower()
    ][:25]


def save_corp_clear_status(corp: str, selected_systems: List[str], pilot_name: str) -> bool:
    try:
        week_date = get_current_week_start_date()
        roster, _ = fetch_alliance_data()
        corp_systems = [system for system, _region in roster.get(corp, [])]
        timestamp = datetime.datetime.now(config.KYIV_TZ).strftime("%Y-%m-%d %H:%M")
        for system in corp_systems:
            is_cleared = system in selected_systems
            status = "Cleared" if is_cleared else "Active"
            cleared_by = pilot_name if is_cleared else ""
            cleared_at = timestamp if is_cleared else ""
            db_manager.update_progress(week_date, corp, system, status, cleared_by, cleared_at)
        return True
    except Exception as error:
        logger.error("❌ Помилка збереження статусу зачистки в БД для %s: %s", corp, error)
        return False

def reset_alliance_current_week() -> bool:
    try:
        week_date = get_current_week_start_date()
        with db_manager._get_connection() as conn:
            conn.execute("DELETE FROM progress WHERE week_date = ?", (week_date,))
            conn.commit()
        return True
    except Exception as error:
        logger.error("❌ Помилка скидання тижня в БД: %s", error)
        return False

async def build_alliance_embed(lang: str = "ua") -> discord.Embed:
    roster, progress = await asyncio.to_thread(fetch_alliance_data)
    current_week = get_current_week_start_date()
    if not roster:
        return discord.Embed(
            title=t("alliance_siege", "title", lang),
            description=t("alliance_siege", "roster_empty", lang, sheet=config.ALLIANCE_ROSTER_SHEET),
            color=discord.Color.red(),
        )
    total_systems = sum(len(systems) for systems in roster.values())
    cleared_systems = 0
    status_lines = []
    for corporation, systems in roster.items():
        corp_total = len(systems)
        corp_cleared = sum(1 for system, _region in systems if progress.get((corporation, system), {}).get("status") == "Cleared")
        cleared_systems += corp_cleared
        icon = "✅" if corp_cleared == corp_total and corp_total > 0 else "⚠️" if corp_cleared > 0 else "🔴"
        status_lines.append(f"{icon} **{corporation}** — {corp_cleared}/{corp_total}")
    percent = int(cleared_systems / total_systems * 100) if total_systems else 0
    description = t("alliance_siege", "desc", lang, date=current_week, cleared_total=cleared_systems, all_total=total_systems, percent=percent, corps_summary="\n".join(status_lines))
    color = discord.Color.green() if cleared_systems == total_systems and total_systems > 0 else discord.Color.gold()
    embed = discord.Embed(title=t("alliance_siege", "title", lang), description=description, color=color)
    embed.set_footer(text=f"Google Sheets: {config.ALLIANCE_ROSTER_SHEET} • Reset every Wednesday at 13:00 Kyiv")
    return embed

class ChangeCorpModal(discord.ui.Modal):
    def __init__(self, system: str, current_corp: str):
        super().__init__(title="Зміна корпорації системи / Change Corp")
        self.system = system
        self.old_corp = current_corp

        self.corp_input = discord.ui.TextInput(
            label="Нова корпорація / New Corp",
            placeholder="Наприклад: UAN",
            required=True
        )
        self.add_item(self.corp_input)

    async def on_submit(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        try:
            new_corp = self.corp_input.value
            region = SYSTEM_REGION_MAP.get(self.system, "Unknown")

            # Remove from old corp, add to new corp
            success_remove = await asyncio.to_thread(sheets_service.remove_roster_row, self.old_corp, self.system)
            success_add = await asyncio.to_thread(sheets_service.update_roster_row, new_corp, self.system, region)

            if not success_add:
                await interaction.response.send_message("❌ Не вдалося оновити дані в Google Sheets", ephemeral=True)
                return

            await asyncio.to_thread(db_manager.remove_system, self.old_corp, self.system)
            await asyncio.to_thread(db_manager.add_system, new_corp, self.system, region)

            await interaction.response.send_message(f"✅ Система {self.system} перенесена з {self.old_corp} до {new_corp}!", ephemeral=True)
        except Exception as error:
            logger.error("⚠️ Error ChangeCorpModal: %s", error)
            await interaction.response.send_message(t("common", "error_occurred", lang), ephemeral=True)

class AssignSystemModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Призначення системи / Assign System")
        self.corp_input = discord.ui.TextInput(label="Корпорація / Corp", placeholder="Наприклад: UAN", required=True)
        self.system_input = discord.ui.TextInput(label="Система / System", placeholder="Наприклад: UDE-FX", required=True)
        self.add_item(self.corp_input)
        self.add_item(self.system_input)

    async def on_submit(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        try:
            corp, system = self.corp_input.value, self.system_input.value
            if system not in SYSTEM_REGION_MAP:
                await interaction.response.send_message(f"❌ Система {system} не знайдена в реєстрі дозволених систем!", ephemeral=True)
                return

            region = SYSTEM_REGION_MAP[system]
            success_sheet = await asyncio.to_thread(sheets_service.update_roster_row, corp, system, region)
            if not success_sheet:
                await interaction.response.send_message("❌ Помилка при додаванні в Google Sheets", ephemeral=True)
                return
            await asyncio.to_thread(db_manager.add_system, corp, system, region)
            await interaction.response.send_message(f"✅ Систему {system} ({region}) призначено корпорації {corp}!", ephemeral=True)
        except Exception as error:
            logger.error("⚠️ Error AssignSystemModal: %s", error)
            await interaction.response.send_message(t("common", "error_occurred", lang), ephemeral=True)

class SystemActionView(discord.ui.View):
    def __init__(self, corp: str, system: str, region: str):
        super().__init__(timeout=300)
        self.corp = corp
        self.system = system
        self.region = region

    @discord.ui.button(label="✏️ Змінити корп / Change Corp", style=discord.ButtonStyle.primary)
    async def edit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChangeCorpModal(self.system, self.corp))

    @discord.ui.button(label="🗑️ Видалити / Remove", style=discord.ButtonStyle.danger)
    async def remove_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        confirm_btn = discord.ui.Button(label="Так, видалити / Yes, remove", style=discord.ButtonStyle.danger)

        async def confirm_callback(int_interaction: discord.Interaction):
            try:
                success_sheet = await asyncio.to_thread(sheets_service.remove_roster_row, self.corp, self.system)
                if not success_sheet:
                    await int_interaction.response.send_message("❌ Не вдалося знайти систему в Sheets", ephemeral=True)
                    return
                await asyncio.to_thread(db_manager.remove_system, self.corp, self.system)
                await int_interaction.response.send_message(f"✅ {self.system} видалено!", ephemeral=True)
            except Exception as e:
                logger.error("⚠️ Error remove: %s", e)
                await int_interaction.response.send_message("❌ Помилка при видаленні", ephemeral=True)

        confirm_btn.callback = confirm_callback
        view.add_item(confirm_btn)
        await interaction.response.send_message(f"⚠️ Ви впевнені, що хочете видалити {self.system} для {self.corp}?", view=view, ephemeral=True)

class SystemSelect(discord.ui.Select):
    def __init__(self, corp: str, systems: List[Tuple[str, str]], lang: str, page: int = 1, page_size: int = 25):
        total_pages = (len(systems) + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_systems = systems[start_index:end_index]

        options = [discord.SelectOption(label=f"{s} — {r}" if r else s, value=s) for s, r in page_systems]
        placeholder = f"({page}/{total_pages}) Оберіть систему / Select system"
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        system = self.values[0]
        roster, _ = await asyncio.to_thread(fetch_alliance_data)
        systems = roster.get(self.view.current_corp, [])
        region = next((r for s, r in systems if s == system), "")

        await interaction.response.send_message(
            f"Керування системою **{system}** ({self.view.current_corp})",
            view=SystemActionView(self.view.current_corp, system, region),
            ephemeral=True
        )

class CorpSelectManage(discord.ui.Select):
    def __init__(self, roster: Dict[str, List[Tuple[str, str]]], lang: str, page: int = 1, page_size: int = 25):
        unique_corps = sorted(list(roster.keys()))
        total_pages = (len(unique_corps) + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_corps = unique_corps[start_index:end_index]

        options = [discord.SelectOption(label=corp[:100], value=corp) for corp in page_corps]
        placeholder = f"({page}/{total_pages}) Оберіть корпорацію / Select corp"
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        corp = self.values[0]
        view: ManageSystemsView = self.view
        view.current_corp = corp
        view.system_page = 1
        view.update_view()
        await interaction.response.edit_message(view=view)

class ManageSystemsView(discord.ui.View):
    def __init__(self, roster: Dict[str, List[Tuple[str, str]]], lang: str, page: int = 1, system_page: int = 1):
        super().__init__(timeout=300)
        self.roster = roster
        self.lang = lang
        self.page = page
        self.system_page = system_page
        self.page_size = 25
        self.current_corp = None
        self.update_view()

    def update_view(self):
        # Remove existing items manually
        self.children.clear()
        if not self.current_corp:
            self.add_item(CorpSelectManage(self.roster, self.lang, page=self.page, page_size=self.page_size))

            # Corp Navigation
            total_pages = (len(self.roster) + self.page_size - 1) // self.page_size
            if self.page > 1:
                btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
                btn_prev.callback = self.prev_page
                self.add_item(btn_prev)
            if self.page < total_pages:
                btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)
                btn_next.callback = self.next_page
                self.add_item(btn_next)
        else:
            systems = self.roster.get(self.current_corp, [])
            self.add_item(SystemSelect(self.current_corp, systems, self.lang, page=self.system_page))

            # System Navigation
            total_pages = (len(systems) + self.page_size - 1) // self.page_size
            if self.system_page > 1:
                btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
                btn_prev.callback = self.prev_system_page
                self.add_item(btn_prev)
            if self.system_page < total_pages:
                btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)
                btn_next.callback = self.next_system_page
                self.add_item(btn_next)

            btn_back = discord.ui.Button(label="🔙 Back to Corps", style=discord.ButtonStyle.secondary)
            btn_back.callback = self.back_to_corps
            self.add_item(btn_back)

    async def prev_page(self, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        self.update_view()
        await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        total_pages = (len(self.roster) + self.page_size - 1) // self.page_size
        if self.page < total_pages:
            self.page += 1
            self.update_view()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()

    async def prev_system_page(self, interaction: discord.Interaction):
        self.system_page = max(1, self.system_page - 1)
        self.update_view()
        await interaction.response.edit_message(view=self)

    async def next_system_page(self, interaction: discord.Interaction):
        systems = self.roster.get(self.current_corp, [])
        total_pages = (len(systems) + self.page_size - 1) // self.page_size
        if self.system_page < total_pages:
            self.system_page += 1
            self.update_view()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()

    async def back_to_corps(self, interaction: discord.Interaction):
        self.current_corp = None
        self.update_view()
        await interaction.response.edit_message(view=self)

class CorpClearSelect(discord.ui.Select):
    def __init__(self, corp: str, systems: List[Tuple[str, str]], progress: Dict, lang: str, page: int = 1, page_size: int = 25):
        total_pages = (len(systems) + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_systems = systems[start_index:end_index]

        options = []
        for system, region in page_systems:
            system_progress = progress.get((corp, system), {})
            is_cleared = system_progress.get("status") == "Cleared"
            cleared_by = system_progress.get("cleared_by", "")
            description = region or "System"
            if is_cleared and cleared_by:
                description += f" (Cleared by {cleared_by})"
            label = f"{system} — {region}" if region else system
            options.append(discord.SelectOption(label=label[:100], value=system, description=description[:100], emoji="✅" if is_cleared else "⚔️", default=is_cleared))

        placeholder = f"({page}/{total_pages}) {t('alliance_siege', 'select_placeholder', lang)}"
        super().__init__(placeholder=placeholder, min_values=0, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        # Update the selected systems list in the view
        current_cleared = set(self.view.selected_systems)
        for option in self.values:
            current_cleared.add(option)

        # This is tricky because the select is multi-select but paginated.
        # To handle this properly, the view needs to track the total state.
        self.view.update_selected_systems(self.values)
        await interaction.response.defer()

class CorpClearModalView(discord.ui.View):
    def __init__(self, corp: str, systems: List[Tuple[str, str]], progress: Dict, lang: str, panel_message: discord.Message):
        super().__init__(timeout=300)
        self.corp = corp
        self.lang = lang
        self.panel_message = panel_message
        self.total_count = len(systems)
        self.systems = systems
        self.progress = progress
        self.page = 1
        self.page_size = 25
        self.selected_systems = [system for system, _region in systems if progress.get((corp, system), {}).get("status") == "Cleared"]
        self.update_view()

    def update_view(self):
        self.children.clear()
        self.add_item(CorpClearSelect(self.corp, self.systems, self.progress, self.lang, page=self.page))

        total_pages = (self.total_count + self.page_size - 1) // self.page_size
        if self.page > 1:
            btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
            btn_prev.callback = self.prev_page
            self.add_item(btn_prev)
        if self.page < total_pages:
            btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)
            btn_next.callback = self.next_page
            self.add_item(btn_next)

    async def prev_page(self, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        self.update_view()
        await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        total_pages = (self.total_count + self.page_size - 1) // self.page_size
        if self.page < total_pages:
            self.page += 1
            self.update_view()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()

    def update_selected_systems(self, selected_on_page: List[str]):
        # This is tricky. Since it's a multi-select, we need to know which ones
        # from the current page were selected and which ones were deselected.
        page_systems = [s for s, _ in self.systems[ (self.page-1)*self.page_size : self.page*self.page_size ]]

        # Remove all current page systems from total selection
        self.selected_systems = [s for s in self.selected_systems if s not in page_systems]
        # Add only the selected ones from current page
        self.selected_systems.extend(selected_on_page)

    @discord.ui.button(label="💾 Save / Зберегти", style=discord.ButtonStyle.success)
    async def save_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        success = await asyncio.to_thread(save_corp_clear_status, self.corp, self.selected_systems, interaction.user.display_name)
        if success:
            try:
                await self.panel_message.edit(embed=await build_alliance_embed(lang=self.lang), view=await AllianceSiegeControlView.create(lang=self.lang))
            except discord.HTTPException as error:
                logger.warning("⚠️ Не вдалося оновити Alliance Siege панель: %s", error)
            await interaction.followup.send(t("alliance_siege", "save_success", self.lang, corp=self.corp, user=interaction.user.mention, cleared=len(self.selected_systems), total=self.total_count), ephemeral=True)
        else:
            await interaction.followup.send(t("common", "error_occurred", self.lang), ephemeral=True)

class CorpSelect(discord.ui.Select):
    def __init__(self, roster: Dict[str, List[Tuple[str, str]]], lang: str, page: int = 1, page_size: int = 20):
        unique_corps = sorted(list(roster.keys()))
        total_pages = (len(unique_corps) + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_corps = unique_corps[start_index:end_index]
        options = [discord.SelectOption(label=corp[:100], value=corp) for corp in page_corps]
        placeholder = t("alliance_siege", "select_placeholder", lang).replace("системи", "корпорацію")
        placeholder = f"({page}/{total_pages}) {placeholder}"
        super().__init__(placeholder=placeholder, options=options, custom_id="all_siege_corp_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        corp = self.values[0]
        lang = get_lang(interaction)
        roster, progress = await asyncio.to_thread(fetch_alliance_data)
        systems = roster.get(corp, [])
        if not systems:
            await interaction.followup.send(f"❌ Немає систем для корпорації {corp} у Google Sheets!", ephemeral=True)
            return
        embed = discord.Embed(title=t("alliance_siege", "corp_title", lang, corp=corp), description=t("alliance_siege", "corp_desc", lang), color=discord.Color.blue())
        await interaction.followup.send(embed=embed, view=CorpClearModalView(corp, systems, progress, lang, interaction.message), ephemeral=True)

class AllianceSiegeControlView(discord.ui.View):
    def __init__(self, lang: str = "ua", current_page: int = 1):
        super().__init__(timeout=None)
        self.lang = lang
        self.current_page = current_page

    @classmethod
    async def create(cls, lang: str = "ua", current_page: int = 1):
        view = cls(lang=lang, current_page=current_page)
        roster, _ = await asyncio.to_thread(fetch_alliance_data)
        view.add_item(CorpSelect(roster, lang, page=current_page))
        if current_page > 1:
            btn_prev = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="all_siege_prev")
            btn_prev.callback = view.prev_page
            view.add_item(btn_prev)
        unique_corps = sorted(list(roster.keys()))
        total_pages = (len(unique_corps) + 19) // 20
        if current_page < total_pages:
            btn_next = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="all_siege_next")
            btn_next.callback = view.next_page
            view.add_item(btn_next)
        btn_refresh = discord.ui.Button(label="🔄 Refresh", style=discord.ButtonStyle.primary, custom_id="all_siege_refresh")
        btn_refresh.callback = view.refresh_callback
        view.add_item(btn_refresh)
        btn_reset = discord.ui.Button(label="⚙️ Reset", style=discord.ButtonStyle.danger, custom_id="all_siege_reset")
        btn_reset.callback = view.reset_callback
        view.add_item(btn_reset)
        return view

    async def refresh_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        lang = get_lang(interaction)
        await asyncio.to_thread(fetch_alliance_data, force_refresh=True)
        await interaction.message.edit(embed=await build_alliance_embed(lang=lang), view=await AllianceSiegeControlView.create(lang=lang, current_page=self.current_page))

    async def reset_callback(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        is_officer = (any(role.id in config.OFFICER_ROLES for role in interaction.user.roles) or interaction.user.guild_permissions.administrator)
        if not is_officer:
            await interaction.response.send_message(t("common", "officer_only", lang), ephemeral=True)
            return
        await interaction.response.defer()
        await asyncio.to_thread(reset_alliance_current_week)
        await interaction.message.edit(embed=await build_alliance_embed(lang=lang), view=await AllianceSiegeControlView.create(lang=lang, current_page=self.current_page))
        await interaction.followup.send(t("siege", "reset_success", lang), ephemeral=True)

    async def prev_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        lang = get_lang(interaction)
        new_page = max(1, self.current_page - 1)
        await interaction.message.edit(embed=await build_alliance_embed(lang=lang), view=await AllianceSiegeControlView.create(lang=lang, current_page=new_page))

    async def next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        lang = get_lang(interaction)
        new_page = self.current_page + 1
        await interaction.message.edit(embed=await build_alliance_embed(lang=lang), view=await AllianceSiegeControlView.create(lang=lang, current_page=new_page))

class AllianceSiege(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.alliance_scheduler.start()
        self.sync_scheduler.start()

    def cog_unload(self):
        self.alliance_scheduler.cancel()
        self.sync_scheduler.cancel()

    async def initial_sync(self):
        logger.info("🚀 Починаємо початкову синхронізацію з Google Sheets...")
        try:
            roster_sheet = get_roster_sheet()
            roster_rows = roster_sheet.get_all_values()
            roster_data = []
            for row in roster_rows[1:]:
                if len(row) >= 3 and row[0].strip() and row[1].strip():
                    roster_data.append((row[0].strip(), row[1].strip(), row[2].strip()))
            db_manager.sync_roster(roster_data)
            progress_sheet = get_progress_sheet()
            progress_rows = progress_sheet.get_all_values()
            progress_data = []
            for row in progress_rows[1:]:
                if len(row) >= 6:
                    progress_data.append(tuple(row))
            db_manager.sync_progress(progress_data)
            logger.info("✅ Початкова синхронізація завершена.")
        except Exception as error:
            logger.error("❌ Помилка під час початкової синхронізації: %s", error)

    @tasks.loop(minutes=1)
    async def alliance_scheduler(self):
        now = datetime.datetime.now(config.KYIV_TZ)
        if now.hour != 13 or now.minute != 0:
            return
        channel = self.bot.get_channel(config.ALLIANCE_SIEGE_CHANNEL_ID)
        if not channel:
            logger.warning("❌ Не знайдено Alliance Siege канал %s", config.ALLIANCE_SIEGE_CHANNEL_ID)
            return
        role_ping = f"<@&{config.SIEGE_ROLE_ID}>" if config.SIEGE_ROLE_ID else ""
        if now.weekday() == 2:
            await asyncio.to_thread(reset_alliance_current_week)
            await channel.send(content=f"📢 {role_ping} **Старт нового осадного тижня Альянсу! / Alliance Siege Week Started!**", embed=await build_alliance_embed(), view=await AllianceSiegeControlView.create())
        else:
            roster, progress = await asyncio.to_thread(fetch_alliance_data)
            total = sum(len(systems) for systems in roster.values())
            cleared = sum(1 for record in progress.values() if record.get("status") == "Cleared")
            if cleared < total and total > 0:
                await channel.send(content=f"⚠️ {role_ping} **Щоденне нагадування Альянсу! / Alliance Siege Reminder:** ({cleared}/{total} зачищено)", embed=await build_alliance_embed(), view=await AllianceSiegeControlView.create())

    @tasks.loop(seconds=config.DB_SYNC_INTERVAL)
    async def sync_scheduler(self):
        logger.info("🔄 Синхронізація БД -> Google Sheets...")
        try:
            week_date = get_current_week_start_date()
            progress_sheet = get_progress_sheet()
            data = await asyncio.to_thread(db_manager.get_pending_updates, week_date)
            if not data:
                return
            all_values = progress_sheet.get_all_values()
            if len(all_values) > 1:
                progress_sheet.batch_clear([f"A2:F{len(all_values)}"])
            progress_set = progress_sheet.append_rows(data)
            logger.info("✅ Дані успішно синхронізовано з Google Sheets.")
        except Exception as error:
            logger.error("❌ Помилка фонової синхронізації: %s", error)

    @alliance_scheduler.before_loop
    async def before_scheduler(self):
        await self.bot.wait_until_ready()
        await self.initial_sync()

    @sync_scheduler.before_loop
    async def before_sync_scheduler(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="init_alliance_siege", description="Ініціалізація панелі осадних флотів альянсу / Initialize Alliance Siege")
    async def init_alliance_siege(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        await interaction.response.defer(ephemeral=True)
        role_ping = f"<@&{config.SIEGE_ROLE_ID}>" if config.SIEGE_ROLE_ID else ""
        await interaction.channel.send(content=f"📢 {role_ping} **Alliance Siege Fleets / Осадні Флоти Альянсу:**", embed=await build_alliance_embed(lang=lang), view=await AllianceSiegeControlView.create(lang=lang))
        await interaction.followup.send("✅ Alliance Siege Panel Initialized!", ephemeral=True)

    @app_commands.command(name="add_system", description="Призначити існуючу систему корпорації / Assign existing system to corp")
    async def add_system(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        is_officer = (any(role.id in config.OFFICER_ROLES for role in interaction.user.roles) or interaction.user.guild_permissions.administrator)
        if not is_officer:
            await interaction.response.send_message(t("common", "officer_only", lang), ephemeral=True)
            return

        await interaction.response.send_modal(AssignSystemModal())

    @app_commands.command(name="edit_system", description="Змінити корпорацію для системи / Change corporation for a system")
    @app_commands.describe(region="Регіон системи", system="Назва системи", new_corp="Нова корпорація")
    @app_commands.autocomplete(region=region_autocomplete, system=system_autocomplete, new_corp=corp_autocomplete)
    async def edit_system(
        self,
        interaction: discord.Interaction,
        region: str,
        system: str,
        new_corp: str
    ):
        lang = get_lang(interaction)
        is_officer = (any(role.id in config.OFFICER_ROLES for role in interaction.user.roles) or interaction.user.guild_permissions.administrator)
        if not is_officer:
            await interaction.response.send_message(t("common", "officer_only", lang), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            if system not in SYSTEM_REGION_MAP:
                await interaction.followup.send(f"❌ Система {system} не знайдена в реєстрі!", ephemeral=True)
                return

            # Verify if the system actually belongs to the selected region to avoid mistakes
            if SYSTEM_REGION_MAP[system] != region:
                await interaction.followup.send(f"❌ Система {system} знаходиться в регіоні {SYSTEM_REGION_MAP[system]}, а не в {region}!", ephemeral=True)
                return

            region_val = SYSTEM_REGION_MAP[system]
            roster, _ = await asyncio.to_thread(fetch_alliance_data)

            # Find current owner
            current_corp = None
            for corp, systems in roster.items():
                if any(s == system for s, _ in systems):
                    current_corp = corp
                    break

            if not current_corp:
                await interaction.followup.send(f"❌ Система {system} зараз не призначена жодній корпорації!", ephemeral=True)
                return

            if current_corp == new_corp:
                await interaction.followup.send(f"⚠️ Система {system} вже належить корпорації {new_corp}!", ephemeral=True)
                return

            # Move: remove from old, add to new
            success_remove = await asyncio.to_thread(sheets_service.remove_roster_row, current_corp, system)
            success_add = await asyncio.to_thread(sheets_service.update_roster_row, new_corp, system, region_val)

            if not success_add:
                await interaction.followup.send("❌ Помилка при оновленні Google Sheets", ephemeral=True)
                return

            await asyncio.to_thread(db_manager.remove_system, current_corp, system)
            await asyncio.to_thread(db_manager.add_system, new_corp, system, region_val)

            await interaction.followup.send(f"✅ Систему {system} перенесено з {current_corp} до {new_corp}!", ephemeral=True)
        except Exception as error:
            logger.error("⚠️ Error edit_system: %s", error)
            await interaction.followup.send(t("common", "error_occurred", lang), ephemeral=True)


    @app_commands.command(name="remove_system", description="Швидке видалення системи (текстом) / Quick remove system (text)")
    @app_commands.describe(region="Регіон системи", system="Назва системи")
    @app_commands.autocomplete(region=region_autocomplete, system=system_autocomplete)
    async def remove_system(
        self,
        interaction: discord.Interaction,
        region: str,
        system: str
    ):
        lang = get_lang(interaction)
        is_officer = (any(role.id in config.OFFICER_ROLES for role in interaction.user.roles) or interaction.user.guild_permissions.administrator)
        if not is_officer:
            await interaction.response.send_message(t("common", "officer_only", lang), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            if system not in SYSTEM_REGION_MAP:
                await interaction.followup.send(f"❌ Система {system} не знайдена в реєстрі!", ephemeral=True)
                return

            if SYSTEM_REGION_MAP[system] != region:
                await interaction.followup.send(f"❌ Система {system} знаходиться в регіоні {SYSTEM_REGION_MAP[system]}, а не в {region}!", ephemeral=True)
                return

            roster, _ = await asyncio.to_thread(fetch_alliance_data)
            current_corp = None
            for corp, systems in roster.items():
                if any(s == system for s, _ in systems):
                    current_corp = corp
                    break

            if not current_corp:
                await interaction.followup.send(f"❌ Система {system} зараз не призначена жодній корпорації!", ephemeral=True)
                return

            success_sheet = await asyncio.to_thread(sheets_service.remove_roster_row, current_corp, system)
            if not success_sheet:
                await interaction.followup.send(f"❌ Не вдалося знайти систему {system} для {current_corp} в Sheets", ephemeral=True)
                return
            await asyncio.to_thread(db_manager.remove_system, current_corp, system)
            await interaction.followup.send(f"✅ {system} (належала {current_corp}) видалено!", ephemeral=True)
        except Exception as error:
            logger.error("⚠️ Error remove_system: %s", error)
            await interaction.followup.send(t("common", "error_occurred", lang), ephemeral=True)


    @app_commands.command(name="manage_systems", description="Керування системами (інтерактивно) / Manage systems (interactive)")
    async def manage_systems(self, interaction: discord.Interaction):
        lang = get_lang(interaction)
        is_officer = (any(role.id in config.OFFICER_ROLES for role in interaction.user.roles) or interaction.user.guild_permissions.administrator)
        if not is_officer:
            await interaction.response.send_message(t("common", "officer_only", lang), ephemeral=True)
            return

        roster, _ = await asyncio.to_thread(fetch_alliance_data)
        await interaction.response.send_message(
            "Оберіть корпорацію для керування системами:",
            view=ManageSystemsView(roster, lang),
            ephemeral=True
        )

    @init_alliance_siege.error
    async def init_alliance_siege_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        logger.error("⚠️ Error init_alliance_siege: %s", error)
        message = t("common", "error_occurred", get_lang(interaction))
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

async def setup(bot: commands.Bot):
    bot.add_view(AllianceSiegeControlView())
    await bot.add_cog(AllianceSiege(bot))
