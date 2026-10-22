from typing import Any, Optional


def get_lang(interaction: Optional[Any] = None) -> str:
    """Return the supported UI language for a Discord interaction."""
    if interaction and getattr(interaction, "locale", None):
        locale = str(interaction.locale).lower()
        if locale in {"uk", "ua", "ukrainian"}:
            return "ua"
    return "en"


STRINGS = {
    "common": {
        "officer_only": {
            "ua": "❌ Доступ заборонено. Тільки для офіцерів корпорації.",
            "en": "❌ Access denied. Corporate officers only.",
        },
        "error_occurred": {
            "ua": "❌ Сталася помилка при обробці запиту.",
            "en": "❌ An error occurred while processing your request.",
        },
        "admin_only": {
            "ua": "❌ У вас немає прав Адміністратора для використання цієї команди!",
            "en": "❌ You do not have Administrator permissions to use this command!",
        },
    },
    "siege": {
        "reset_success": {
            "ua": "⚠️ Усі системи поточного тижня скинуто!",
            "en": "⚠️ All current week systems have been reset!",
        },
    },
    "alliance_siege": {
        "title": {
            "ua": "⚔️ Осадні Флоти Альянсу / Pirate Siege Fleet Reporting",
            "en": "⚔️ Pirate Siege Fleet Reporting",
        },
        "desc": {
            "ua": (
                "⚔️ **Поточний осадний тиждень** (з `{date}`)\n"
                "Загальний прогрес альянсу: **{cleared_total}/{all_total}** ({percent}%)\n\n"
                "📌 **Стан систем по корпораціях / альянс-мемберах:**\n{corps_summary}\n\n"
                "Натисніть кнопку вашої корпорації нижче, щоб відмітити закриті системи."
            ),
            "en": (
                "⚔️ **Current Siege Week** (since `{date}`)\n"
                "Alliance Overall Progress: **{cleared_total}/{all_total}** ({percent}%)\n\n"
                "📌 **Corporation / Member Status:**\n{corps_summary}\n\n"
                "Click your corporation button below to report cleared systems."
            ),
        },
        "corp_title": {
            "ua": "👾 {corp} clear / Зачистка систем",
            "en": "👾 {corp} clear",
        },
        "corp_desc": {
            "ua": "Оберіть системи, які закриті цього тижня:",
            "en": "Select systems cleared this week:",
        },
        "select_placeholder": {
            "ua": "Оберіть системи зі списку...",
            "en": "Select cleared systems from list...",
        },
        "save_success": {
            "ua": "✅ Системи корпорації **{corp}** оновлено пілотом {user}! ({cleared}/{total} зачищено)",
            "en": "✅ Systems for **{corp}** updated by {user}! ({cleared}/{total} cleared)",
        },
        "roster_empty": {
            "ua": "⚠️ Реєстр альянсу порожній. Додайте корпорації та системи у вкладку Google Sheets `{sheet}`!",
            "en": "⚠️ Alliance roster is empty. Add corporations and systems in Google Sheets `{sheet}`!",
        },
    },
}


def t(category: str, key: str, lang: str = "ua", **kwargs: Any) -> str:
    """Get a localized string with optional named formatting arguments."""
    item = STRINGS.get(category, {}).get(key, {})
    if isinstance(item, dict):
        text = item.get(lang, item.get("en", item.get("ua", f"[{category}.{key}]")))
    else:
        text = str(item)

    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, ValueError):
        return text
