import logging
import os
import sys

import telegram.ext
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from src.app.app import App
from src.constants import envars
from src.exceptions import *


class Bot:
    _job_name_poll = '_poll_storehouses'

    def __init__(self):
        logging.basicConfig(stream=sys.stdout,
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        self._logger = logging.getLogger(__name__)

        self._app = App()

        users_whitelist = os.environ[envars.USERS_WHITELIST]
        if not users_whitelist:
            raise RuntimeError(f'Users whitelist not set in {envars.USERS_WHITELIST}')

        self._users_whitelist = set(users_whitelist.split(';'))

        admin_users = os.environ[envars.ADMIN_USERS]
        if not admin_users:
            raise RuntimeError(f'Admin users not set in {envars.ADMIN_USERS}')

        self._admin_users = set(admin_users.split(';'))

    async def _subscribe(self, update: Update, context_types: ContextTypes.DEFAULT_TYPE) -> None:
        uname = update.effective_user.name
        chat_id = update.message.chat_id
        if self._app.handle_subscribe(chat_id, uname):
            await update.message.reply_text("Успешно подписались на оповещения")
        else:
            await update.message.reply_text("Ошибка, не удалось подписаться на оповещения")

    async def _unsubscribe(self, update: Update, context_types: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        if self._app.handle_unsubscribe(chat_id):
            await update.message.reply_text("Успешно отписались от оповещений")
        else:
            await update.message.reply_text("Ошибка, не удалось отписаться от оповещений")

    async def _poll_storehouses(self, context: telegram.ext.CallbackContext):
        self._logger.info('Run poll_storehouses')
        is_found, is_error = self._app.poll_storehouses()
        self._logger.info(f'Poll storehouses is_found={is_found}, is_error={is_error}')
        if is_found or is_error:
            subscriptions = self._app.get_subscriptions()
            for chat_id in subscriptions:
                if is_found:
                    await context.bot.send_message(chat_id, 'Открыт старт продаж!')
                if is_error:
                    await context.bot.send_message(chat_id, '⚠️ Произошла ошибка во время проверки '
                                                            'доступности кладовых')

    async def _get_report(self, update: Update, context_types: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            self._assert_admin(update)
        except CommandNotAllowedException:
            self._logger.exception('Unauthorized reports request')
            await update.message.reply_text('У вас нет доступа к отчётам 🚫')
            return

        reports = self._app.get_report(50)

        await update.message.reply_text(reports, parse_mode='Markdown')

    def run(self):
        self._logger.info("Starting bot, acquiring token")
        bot_token = os.environ[envars.TG_BOT_TOKEN]
        if not bot_token:
            msg = f'Telegram token unset in {envars.TG_BOT_TOKEN}'
            self._logger.error(msg)
            raise RuntimeError(msg)

        self._logger.info("Building app")
        bot_app = ApplicationBuilder().token(bot_token).build()
        job_queue = bot_app.job_queue
        job_queue.run_repeating(self._poll_storehouses, interval=10, name=self._job_name_poll)

        self._logger.info("Registering command handlers")
        bot_app.add_handler(CommandHandler('subscribe', self._subscribe))
        bot_app.add_handler(CommandHandler('unsubscribe', self._unsubscribe))
        bot_app.add_handler(CommandHandler('reports', self._get_report))

        self._logger.info("Start polling")
        bot_app.run_polling()

    def _assert_admin(self, update: Update):
        username = update.effective_user.name
        if username not in self._admin_users:
            raise CommandNotAllowedException()


if __name__ == '__main__':
    Bot().run()
