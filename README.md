# Alli_Bot — Alliance Siege у власному контейнері

`Alli_Bot` — окремий Discord-бот, який обслуговує лише модуль осадних флотів альянсу. Він замінив `cogs/alliance_siege.py` у головному Budanow Eye, але може використовувати ті самі вкладки Google Sheets: `Alliance_Roster` і `Alliance_Siege`.

## Що ізольовано

- окремий Discord bot token і власне дерево slash-команд;
- окремий `.env` та `credentials.json` у цій папці;
- окремий Docker-образ і контейнер `budanow_alliance_siege`;
- лише потрібні залежності: Discord, Google Sheets, dotenv і часова база;
- власні `services/sheets.py` та `services/localization.py`.

Головний бот більше не завантажує Alliance Siege. Не запускайте обидва боти з одним `DISCORD_TOKEN`: для цього сервісу створіть окремий Discord application/bot і запросіть його на сервер.

## Швидкий запуск у Docker

1. Перейдіть до папки сервісу:

   ```bash
   cd Alli_Bot
   ```

2. Створіть конфігурацію та заповніть реальні значення:

   ```bash
   cp .env.example .env
   ```

3. Помістіть service-account JSON у `Alli_Bot/credentials.json`. Його можна використати з головного бота, якщо цей service account уже має доступ редактора до потрібної таблиці Google.

4. Запустіть контейнер:

   ```bash
   docker compose up -d --build
   docker compose logs -f alliance-siege-bot
   ```

5. У цільовому Discord-каналі виконайте `/init_alliance_siege`. Це може зробити будь-хто, хто бачить канал і має право використовувати slash-команди; новий бот опублікує робочу панель.

## Конфігурація `.env`

| Змінна | Обов'язкова | Призначення |
| --- | --- | --- |
| `DISCORD_TOKEN` | Так | Токен окремого Discord-бота Alliance Siege. |
| `GOOGLE_CREDS_FILE` | Ні | Шлях до service-account JSON; типове значення — `credentials.json`. |
| `SPREADSHEET_ID` | Так | ID Google Spreadsheet із вкладками альянсу. |
| `ALLIANCE_SIEGE_CHANNEL_ID` | Так | Канал для автоматичних повідомлень і стартової панелі. |
| `OFFICER_ROLE_IDS` | Ні | Discord ID офіцерських ролей через кому; вони можуть скинути тиждень. Discord Administrator також має це право. |
| `SIEGE_ROLE_ID` | Ні | Роль для щоденних/щотижневих згадок; `0` вимикає згадку ролі. |
| `ALLIANCE_ROSTER_SHEET` | Ні | Назва вкладки реєстру; типово `Alliance_Roster`. |
| `ALLIANCE_SIEGE_SHEET` | Ні | Назва вкладки прогресу; типово `Alliance_Siege`. |

Мінімальний приклад:

```dotenv
DISCORD_TOKEN=your_dedicated_alliance_bot_token
GOOGLE_CREDS_FILE=credentials.json
SPREADSHEET_ID=your_spreadsheet_id
ALLIANCE_SIEGE_CHANNEL_ID=123456789012345678
OFFICER_ROLE_IDS=123456789012345678,234567890123456789
SIEGE_ROLE_ID=345678901234567890
```

Під час старту бот перевіряє наявність `DISCORD_TOKEN`, `SPREADSHEET_ID`, `ALLIANCE_SIEGE_CHANNEL_ID` і файлу `GOOGLE_CREDS_FILE`; з неповною конфігурацією він не підключається.

## Права Discord

Для бота потрібні:

- `View Channel`, `Send Messages`, `Embed Links`;
- `Use Application Commands`;
- `Read Message History`;
- право надсилати повідомлення в цільовий канал;
- OAuth2 scopes `bot` та `applications.commands` під час запрошення на сервер.

Модуль не використовує Message Content або Server Members privileged intents. Права керування ролями й каналами не потрібні.

## Дані Google Sheets

### `Alliance_Roster`

| Member / Corp | System | Region |
| --- | --- | --- |
| UAN | UDE-FX | Insmother |

Кожен рядок описує одну систему, відповідальну за корпорацію або окремого члена альянсу. Якщо вкладка створюється порожньою, бот додає демонстраційний `DEFAULT_ROSTER_SAMPLE`; замініть його реальним реєстром перед бойовим використанням.

### `Alliance_Siege`

| Week Date | Member / Corp | System | Status | Cleared By | Cleared At |
| --- | --- | --- | --- | --- | --- |
| 2026-09-16 | UAN | UDE-FX | Cleared | PilotName | 2026-09-16 13:05 |

Дані записуються для поточного осадного тижня. Ключ тижня — дата середи; новий тиждень починається о 13:00 за `Europe/Kyiv`.

## Як працює модуль

1. Будь-який учасник із доступом до каналу створює панель `/init_alliance_siege`.
2. Кожна корпорація має кнопку зі співвідношенням `закрито / всього`.
3. Учасник вибирає закриті системи в тимчасовому приватному селекті й натискає «Зберегти».
4. Бот записує для кожної системи `Cleared` або `Active`, автора та час, а потім одразу оновлює публічну панель із новим прогресом.
5. Офіцерська роль або Discord Administrator може скинути статуси поточного тижня.

Дані з Google Sheets кешуються на 15 секунд, щоб не створювати надмірних запитів при оновленні панелі.

## Автоматизація

Щодня о **13:00 Europe/Kyiv**:

- у середу бот скидає всі статуси поточного тижня та надсилає панель нового тижня;
- з четверга до вівторка бот нагадує про незакриті системи, якщо такі є.

Якщо сервіс був вимкнений саме в цю хвилину, пропущена дія не запускається заднім числом.

## Локальний запуск без Docker

```bash
cd Alli_Bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Відомі межі Discord UI

- На головній панелі відображається максимум 20 корпорацій (чотири ряди по п'ять кнопок).
- Селект однієї корпорації показує максимум 25 систем.
- Будь-який учасник, який бачить панель, наразі може зберегти статус корпорації; перевірка належності користувача до конкретної корпорації не реалізована.
