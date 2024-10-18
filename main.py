import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Recupera o token do bot do arquivo .env ou ambiente
my_secret = os.getenv('token')  # Carrega o token do arquivo .env
my_secret = os.environ['token']  # Para Replit (ou outro ambiente)

# Configura o logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Traduções para múltiplos idiomas
LANGUAGES = {
    'en': {
        'greeting': "Hi! Choose an option:",
        'mtproto_button': "MTProto Proxies",
        'socks_button': "SOCKS Proxies",
        'language_changed': "Language changed to English.",
        'mtproto_msg': "Here are your MTProto proxies:",
        'socks_msg': "Here are your SOCKS proxies:",
        'language_options': "Choose your language: English (en), Portuguese (pt), Russian (ru), Arabic (ar), Spanish (es), Chinese (zh)",
        'choose_language': "Please choose your language:"
    },
    'pt': {
        'greeting': "Olá! Escolha uma opção:",
        'mtproto_button': "Proxies MTProto",
        'socks_button': "Proxies SOCKS",
        'language_changed': "Idioma alterado para português.",
        'mtproto_msg': "Aqui estão seus proxies MTProto:",
        'socks_msg': "Aqui estão seus proxies SOCKS:",
        'language_options': "Escolha seu idioma: Inglês (en), Português (pt), Russo (ru), Árabe (ar), Espanhol (es), Chinês (zh)",
        'choose_language': "Por favor, escolha seu idioma:"
    },
    'ru': {
        'greeting': "Привет! Выберите опцию:",
        'mtproto_button': "MTProto прокси",
        'socks_button': "SOCKS прокси",
        'language_changed': "Язык изменён на русский.",
        'mtproto_msg': "Вот ваши MTProto прокси:",
        'socks_msg': "Вот ваши SOCKS прокси:",
        'language_options': "Выберите язык: Английский (en), Португальский (pt), Русский (ru), Арабский (ar), Испанский (es), Китайский (zh)",
        'choose_language': "Пожалуйста, выберите язык:"
    },
    'ar': {
        'greeting': "مرحبًا! اختر خيارًا:",
        'mtproto_button': "بروكسي MTProto",
        'socks_button': "بروكسي SOCKS",
        'language_changed': "تم تغيير اللغة إلى العربية.",
        'mtproto_msg': "ها هي بروكسيات MTProto الخاصة بك:",
        'socks_msg': "ها هي بروكسيات SOCKS الخاصة بك:",
        'language_options': "اختر لغتك: الإنجليزية (en), البرتغالية (pt), الروسية (ru), العربية (ar), الإسبانية (es), الصينية (zh)",
        'choose_language': "يرجى اختيار لغتك:"
    },
    'es': {
        'greeting': "¡Hola! Elige una opción:",
        'mtproto_button': "Proxies MTProto",
        'socks_button': "Proxies SOCKS",
        'language_changed': "Idioma cambiado a español.",
        'mtproto_msg': "Aquí están tus proxies MTProto:",
        'socks_msg': "Aquí están tus proxies SOCKS:",
        'language_options': "Elige tu idioma: Inglés (en), Portugués (pt), Ruso (ru), Árabe (ar), Español (es), Chino (zh)",
        'choose_language': "Por favor, elige tu idioma:"
    },
    'zh': {
        'greeting': "你好！选择一个选项：",
        'mtproto_button': "MTProto代理",
        'socks_button': "SOCKS代理",
        'language_changed': "语言已更改为中文。",
        'mtproto_msg': "这是您的MTProto代理：",
        'socks_msg': "这是您的SOCKS代理：",
        'language_options': "选择您的语言：英语 (en), 葡萄牙语 (pt), 俄语 (ru), 阿拉伯语 (ar), 西班牙语 (es), 中文 (zh)",
        'choose_language': "请选择您的语言："
    }
}

# Função para converter timestamps em datas legíveis
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Função para buscar proxies MTProto
def fetch_mtproto_links():
    try:
        response = requests.get("https://mtpro.xyz/api/?type=mtproto")
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching MTProto proxies: {e}")
        return [], "Error fetching MTProto proxies. Please try again later."

    if data and isinstance(data, list):
        filtered_proxies = sorted(
            [proxy_info for proxy_info in data if proxy_info.get('ping', float('inf')) <= 1000],
            key=lambda x: x['ping']
        )[:10]  # Limitar a 10 proxies

        # Criar botões com informações detalhadas para os proxies MTProto
        buttons = []
        proxy_info_texts = []
        for proxy_info in filtered_proxies:
            host = proxy_info['host']
            port = proxy_info['port']
            secret = proxy_info['secret']
            country = proxy_info.get('country', 'N/A')
            ping = proxy_info['ping']
            uptime = proxy_info.get('uptime', 'N/A')
            add_time = convert_timestamp(proxy_info['addTime'])
            up_speed = proxy_info.get('up', 'N/A')
            down_speed = proxy_info.get('down', 'N/A')

            # Texto a ser exibido para cada proxy
            proxy_info_text = (
                f"🌍 País: {country}\n"
                f"🔗 Host: {host}\n"
                f"🚪 Porta: {port}\n"
                f"🔑 Segredo: {secret}\n"
                f"📈 Uptime: {uptime}%\n"
                f"📶 Ping: {ping} ms\n"
                f"📤 Upload: {up_speed} Mbps\n"
                f"📥 Download: {down_speed} Mbps\n"
                f"📅 Adicionado em: {add_time}"
            )
            proxy_info_texts.append(proxy_info_text)

            # Adiciona botões para os proxies
            buttons.append(
                [InlineKeyboardButton(f"Conectar a {host}", url=f"https://t.me/proxy?server={host}&port={port}&secret={secret}")]
            )

        # Adiciona botões de atualizar e trocar protocolo
        buttons.append([InlineKeyboardButton("🔄 Atualizar MTProto", callback_data='mtproto')])
        buttons.append([InlineKeyboardButton("Trocar para SOCKS", callback_data='socks')])
        return buttons, "\n\n".join(proxy_info_texts)

    logging.error("Resposta inválida da API MTProto.")
    return [], "Erro: Resposta inválida da API MTProto."


# Função para buscar proxies SOCKS
def fetch_socks_links():
    try:
        response = requests.get("https://mtpro.xyz/api/?type=socks")
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching SOCKS proxies: {e}")
        return [], "Error fetching SOCKS proxies. Please try again later."

    if data and isinstance(data, list):
        filtered_proxies = sorted(
            [proxy_info for proxy_info in data if proxy_info.get('ping', float('inf')) <= 1000],
            key=lambda x: x['ping']
        )[:8]  # Limitar a 8 proxies

        # Criar botões com informações detalhadas para os proxies SOCKS
        buttons = []
        proxy_info_texts = []
        for proxy_info in filtered_proxies:
            ip = proxy_info['ip']
            port = proxy_info['port']
            country = proxy_info.get('country', 'N/A')
            ping = proxy_info['ping']
            add_time = convert_timestamp(proxy_info['addTime'])

            # Texto a ser exibido para cada proxy SOCKS
            proxy_info_text = (
                f"🌍 País: {country}\n"
                f"🔗 IP: {ip}\n"
                f"🚪 Porta: {port}\n"
                f"📶 Ping: {ping} ms\n"
                f"📅 Adicionado em: {add_time}"
            )
            proxy_info_texts.append(proxy_info_text)

            # Adiciona botões para os proxies SOCKS
            buttons.append(
                [InlineKeyboardButton(f"Conectar a {ip}", url=f"tg://socks?server={ip}&port={port}&bot=@mtpro_xyz_bot")]
            )

        # Adiciona botões de atualizar e trocar protocolo
        buttons.append([InlineKeyboardButton("🔄 Atualizar SOCKS", callback_data='socks')])
        buttons.append([InlineKeyboardButton("Trocar para MTProto", callback_data='mtproto')])
        return buttons, "\n\n".join(proxy_info_texts)

    logging.error("Resposta inválida da API SOCKS.")
    return [], "Erro: Resposta inválida da API SOCKS."


# Comando /start para mostrar botões de idioma ao usuário
async def start(update: Update, context: CallbackContext) -> None:
    """Sends language selection buttons."""
    keyboard = [
        [InlineKeyboardButton("🏴󠁧󠁢󠁥󠁮󠁧󠁿 English", callback_data='lang_en'),
         InlineKeyboardButton("🇧🇷 Português", callback_data='lang_pt')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
         InlineKeyboardButton("🇵🇸 العربية", callback_data='lang_ar')],
        [InlineKeyboardButton("🇦🇷 Español", callback_data='lang_es'),
         InlineKeyboardButton("🇨🇳 中文", callback_data='lang_zh')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose your language:", reply_markup=reply_markup)


# Callback handler para gerenciar cliques nos botões
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_language = context.user_data.get('language', 'en')
    translation = LANGUAGES[user_language]

    if query.data.startswith('lang_'):
        selected_language = query.data.split('_')[1]
        context.user_data['language'] = selected_language
        await query.message.reply_text(LANGUAGES[selected_language]['language_changed'])

        # Atualiza os botões com o novo idioma
        translation = LANGUAGES[selected_language]
        keyboard = [
            [InlineKeyboardButton(translation['mtproto_button'], callback_data='mtproto')],
            [InlineKeyboardButton(translation['socks_button'], callback_data='socks')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(translation['greeting'], reply_markup=reply_markup)

    elif query.data == 'mtproto':
        buttons, proxy_info_text = fetch_mtproto_links()
        if proxy_info_text:
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.reply_text(f"{translation['mtproto_msg']}\n\n{proxy_info_text}", reply_markup=reply_markup)

    elif query.data == 'socks':
        buttons, proxy_info_text = fetch_socks_links()
        if proxy_info_text:
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.reply_text(f"{translation['socks_msg']}\n\n{proxy_info_text}", reply_markup=reply_markup)


# Função principal para executar o bot
def main() -> None:
    application = Application.builder().token(my_secret).build()

    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
