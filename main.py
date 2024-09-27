import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue
import os

# Constants
MTPROTO_API_URL = "https://mtpro.xyz/api/?type=mtproto"
SOCKS_API_URL = "https://mtpro.xyz/api/?type=socks"
PING_LIMIT = 1000
MTPROTO_LIMIT = 8
SOCKS_LIMIT = 10
REFRESH_INTERVAL = 1800  # 30 minutes in seconds
my_secret = os.environ['token']

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

# Function to handle API requests
async def fetch_proxies(url: str, limit: int) -> list:
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return sorted(
                [proxy for proxy in data if proxy.get('ping', float('inf')) <= PING_LIMIT],
                key=lambda x: x['ping']
            )[:limit]
        else:
            logging.error(f"Invalid response from API at {url}")
            return []
    except requests.RequestException as e:
        logging.error(f"Error fetching proxies from {url}: {e}")
        return []

# Helper function to create buttons
def create_proxy_buttons(proxies: list, is_mtproto: bool) -> list:
    buttons = []
    for proxy_info in proxies:
        if is_mtproto:
            proxy_link = f"https://t.me/proxy?server={proxy_info['host']}&port={proxy_info['port']}&secret={proxy_info['secret']}"
            label = f"Connect to {proxy_info['host']}"
        else:
            proxy_link = f"tg://socks?server={proxy_info['ip']}&port={proxy_info['port']}&bot=@mtpro_xyz_bot"
            label = f"Connect to {proxy_info['ip']}"
        buttons.append([InlineKeyboardButton(label, url=proxy_link)])

    return buttons

# Function to fetch MTProto proxies
async def fetch_mtproto_links() -> (list, str):
    proxies = await fetch_proxies(MTPROTO_API_URL, MTPROTO_LIMIT)
    if proxies:
        buttons = create_proxy_buttons(proxies, is_mtproto=True)
        buttons.append([InlineKeyboardButton("🔄 Refresh MTProto List", callback_data='mtproto')])
        buttons.append([InlineKeyboardButton("Switch to SOCKS5", callback_data='socks')])
        return buttons, None
    return [], "Error fetching MTProto proxies. Please try again later."

# Function to fetch SOCKS proxies
async def fetch_socks_links() -> (list, str):
    proxies = await fetch_proxies(SOCKS_API_URL, SOCKS_LIMIT)
    if proxies:
        buttons = create_proxy_buttons(proxies, is_mtproto=False)
        buttons.append([InlineKeyboardButton("🔄 Refresh SOCKS List", callback_data='socks')])
        buttons.append([InlineKeyboardButton("Switch to MTProto", callback_data='mtproto')])
        return buttons, None
    return [], "Error fetching SOCKS proxies. Please try again later."

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[
        InlineKeyboardButton("MTProto", callback_data='mtproto'),
        InlineKeyboardButton("SOCKS5", callback_data='socks'),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha o protocolo:", reply_markup=reply_markup)

# Callback handler for buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'mtproto':
        buttons, error_message = await fetch_mtproto_links()
    elif query.data == 'socks':
        buttons, error_message = await fetch_socks_links()

    if error_message:
        await query.message.reply_text(error_message)
    else:
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_reply_markup(reply_markup=reply_markup)

# Auto-refresh job to refresh proxies
async def auto_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_queue = context.job_queue
    job_queue.run_repeating(callback=send_refresh_message, interval=REFRESH_INTERVAL, context=chat_id)
    await update.message.reply_text(f"Auto-refresh enabled. Proxy list will refresh every {REFRESH_INTERVAL // 60} minutes.")

# Helper function to send refreshed proxies
async def send_refresh_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.context
    buttons, _ = await fetch_mtproto_links()  # or fetch_socks_links() if needed
    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=chat_id, text="Proxy list has been refreshed:", reply_markup=reply_markup)

# Run the bot
def main() -> None:
    application = Application.builder().token(my_secret).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("auto_refresh", auto_refresh))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
