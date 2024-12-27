# Código del bot de Telegram
# Configuración del bot

from telegram.ext import Updater, CommandHandler
from managers.assets_manager import obtener_precio_reciente

def precio(update, context):
    simbolo = context.args[0].upper() if context.args else None
    if simbolo:
        precio = obtener_precio_reciente(simbolo)
        if precio:
            update.message.reply_text(f"El precio más reciente de {simbolo} es {precio[0]} (Fecha: {precio[1]})")
        else:
            update.message.reply_text(f"No hay datos para {simbolo}.")
    else:
        update.message.reply_text("Por favor, especifica un activo. Ejemplo: /precio oro")

def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("precio", precio))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

