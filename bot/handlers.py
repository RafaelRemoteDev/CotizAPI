import telebot
from config import TELEGRAM_BOT_TOKEN, ASSETS_DICT
from managers.assets_manager import (
    get_current_price_db,
    update_prices_efficiently,
    calculate_variations,
    update_single_price
)
from services.yahoo_finance import get_current_price as yahoo_get_current_price
from loguru import logger
from datetime import datetime


def setup_bot_handlers(bot: telebot.TeleBot):
    """
    Set up Telegram bot handlers.

    Args:
    ----
        bot: Telegram bot instance.
    """
    if not bot:
        logger.warning("Telegram token not configured, handlers will not be set up")
        return

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.reply_to(message,
                     "¡Hola! Soy CotizAPI Bot.\n\n"
                     "Comandos disponibles:\n"
                     "/assets - Ver precios actuales de activos.\n"
                     "/daily - Variaciones diarias de precios.\n"
                     "/weekly - Variaciones semanales de precios.\n"
                     "/monthly - Variaciones mensuales de precios.\n"
                     "/update - Actualizar precios en la base de datos.\n"
                     "/alerts - Ver alertas generadas en las últimas 24 horas.\n"
                     )

    @bot.message_handler(commands=['assets'])
    def assets(message):
        bot.reply_to(message, "Obteniendo precios actuales desde Yahoo Finance...")

        response = []
        for symbol, name in ASSETS_DICT.items():
            # Get direct price from Yahoo Finance
            price = yahoo_get_current_price(symbol)

            if price is not None:
                # Save to database
                today = datetime.now().strftime('%Y-%m-%d')
                update_single_price(symbol, price, today)
                response.append(f"{name}: {price:.2f} USD")
            else:
                # Try to get from database
                db_price = get_current_price_db(symbol)
                if db_price is not None:
                    response.append(f"{name}: {db_price:.2f} USD (de la base de datos)")
                else:
                    response.append(f"{name}: Precio no disponible.")

        bot.reply_to(message, "\n".join(response))

    @bot.message_handler(commands=['update'])
    def update_cmd(message):
        bot.reply_to(message, "Actualizando precios desde Yahoo Finance uno por uno...")

        try:
            result = update_prices_efficiently(force_update=True)

            response = [
                f"Actualización completada:",
                f"- Total de activos: {result['total_assets']}",
                f"- Actualizados correctamente: {result['updated_successfully']}",
                f"- Activos con error: {result['failed_assets']}"
            ]

            if result['failed_assets'] > 0:
                response.append(f"- Símbolos con error: {', '.join(result['failed_symbols'])}")

            bot.reply_to(message, "\n".join(response))
        except Exception as e:
            logger.error(f"Error updating prices: {e}")
            bot.reply_to(message, f"Error al actualizar precios: {str(e)}")

    @bot.message_handler(commands=['alerts'])
    def alerts_cmd(message):
        from managers.alerts_manager import get_recent_alerts

        try:
            alert_list = get_recent_alerts()

            if not alert_list:
                bot.reply_to(message, "No hay alertas registradas en las últimas 24 horas.")
                return

            response = [
                f"Alerta para {alert['symbol']}! {alert['message']} (Fecha: {alert['date']})"
                for alert in alert_list
            ]

            bot.reply_to(message, "\n".join(response))
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            bot.reply_to(message, f"Error al obtener alertas: {str(e)}")

    @bot.message_handler(commands=['daily'])
    def daily_cmd(message):
        try:
            bot.reply_to(message, "Calculando variaciones diarias...")

            variations = calculate_variations(list(ASSETS_DICT.keys()), 1)

            messages = []
            for var in variations:
                symbol = var["symbol"]
                name = ASSETS_DICT.get(symbol, symbol)

                if var["variation"] is not None:
                    if var["variation"] > 0:
                        prefix = "+"
                    elif var["variation"] < 0:
                        prefix = ""
                    else:
                        prefix = ""
                    messages.append(f"{name}: {prefix}{var['variation']:.2f}%")
                else:
                    messages.append(f"{name}: Datos insuficientes para calcular variación.")

            bot.reply_to(message, "\n".join(messages))
        except Exception as e:
            logger.error(f"Error calculating daily variations: {e}")
            bot.reply_to(message, f"Error al calcular variaciones: {str(e)}")

    @bot.message_handler(commands=['weekly'])
    def weekly_cmd(message):
        try:
            bot.reply_to(message, "Calculando variaciones semanales...")

            variations = calculate_variations(list(ASSETS_DICT.keys()), 7)

            messages = []
            for var in variations:
                symbol = var["symbol"]
                name = ASSETS_DICT.get(symbol, symbol)

                if var["variation"] is not None:
                    if var["variation"] > 0:
                        prefix = "+"
                    elif var["variation"] < 0:
                        prefix = ""
                    else:
                        prefix = ""
                    messages.append(f"{name}: {prefix}{var['variation']:.2f}%")
                else:
                    messages.append(f"{name}: Datos insuficientes para calcular variación.")

            bot.reply_to(message, "\n".join(messages))
        except Exception as e:
            logger.error(f"Error calculating weekly variations: {e}")
            bot.reply_to(message, f"Error al calcular variaciones: {str(e)}")

    @bot.message_handler(commands=['monthly'])
    def monthly_cmd(message):
        try:
            bot.reply_to(message, "Calculando variaciones mensuales...")

            variations = calculate_variations(list(ASSETS_DICT.keys()), 30)

            messages = []
            for var in variations:
                symbol = var["symbol"]
                name = ASSETS_DICT.get(symbol, symbol)

                if var["variation"] is not None:
                    if var["variation"] > 0:
                        prefix = "+"
                    elif var["variation"] < 0:
                        prefix = ""
                    else:
                        prefix = ""
                    messages.append(f"{name}: {prefix}{var['variation']:.2f}%")
                else:
                    messages.append(f"{name}: Datos insuficientes para calcular variación.")

            bot.reply_to(message, "\n".join(messages))
        except Exception as e:
            logger.error(f"Error calculating monthly variations: {e}")
            bot.reply_to(message, f"Error al calcular variaciones: {str(e)}")

    @bot.message_handler(commands=['price'])
    def price_cmd(message):
        # Extract symbol from message (e.g. /price BTC-USD)
        parts = message.text.split()

        if len(parts) < 2:
            bot.reply_to(message, "Por favor, especifica un símbolo. Ejemplo: /price BTC-USD")
            return

        symbol = parts[1].upper()

        if symbol not in ASSETS_DICT:
            symbols_list = ", ".join(ASSETS_DICT.keys())
            bot.reply_to(message, f"Símbolo no reconocido. Símbolos disponibles: {symbols_list}")
            return

        bot.reply_to(message, f"Consultando precio actual de {ASSETS_DICT[symbol]}...")

        # Get direct price from Yahoo Finance
        price = yahoo_get_current_price(symbol)

        if price is not None:
            # Save to database
            today = datetime.now().strftime('%Y-%m-%d')
            update_single_price(symbol, price, today)
            bot.reply_to(message,
                         f"{ASSETS_DICT[symbol]}: {price:.2f} USD (Actualizado: {datetime.now().strftime('%H:%M:%S')})")
        else:
            # Try to get from database
            db_price = get_current_price_db(symbol)
            if db_price is not None:
                bot.reply_to(message, f"{ASSETS_DICT[symbol]}: {db_price:.2f} USD (de la base de datos)")
            else:
                bot.reply_to(message, f"{ASSETS_DICT[symbol]}: Precio no disponible.")

    # Handler for unrecognized commands
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        if message.text.startswith('/'):
            bot.reply_to(message, "Comando no reconocido. Usa /start para ver la lista de comandos disponibles.")
        else:
            bot.reply_to(message, "No entiendo ese mensaje. Usa /start para ver la lista de comandos disponibles.")

    logger.info("Telegram bot handlers configured successfully")
