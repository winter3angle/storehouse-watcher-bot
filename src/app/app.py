import logging
from datetime import datetime, timezone

import humanfriendly

import src.checks as checker
import src.parsing as parser
from src.dal import dal
from src.pik import pikclient as pc


class App:
    def __init__(self):
        self._pik_client = pc.PikClient()
        self._dal = dal.Dal()
        self._logger = logging.getLogger(__name__)

    def handle_subscribe(self, chat_id: int, effective_user_name: str) -> bool:
        self._logger.info('Handling subscription request')
        try:
            subscr_id = self._dal.try_store_subscription(chat_id, effective_user_name)
            if subscr_id:
                self._logger.info(f'Subscription = {subscr_id} for {effective_user_name}')
                return True
            else:
                self._logger.error(f'Failed to subscribe {effective_user_name}')
                return False
        except Exception as e:
            self._logger.exception('Exception during handle_subscribe')
            return False

    def handle_unsubscribe(self, chat_id: int) -> bool:
        self._logger.info('Handling unsubscribe request')
        try:
            self._dal.delete_subscription(chat_id)
            return True
        except:
            self._logger.exception(f'Failed to unsubscribe {chat_id}')
            return False

    def get_report(self, limit: int = 10) -> str:
        self._logger.info(f'Querying recent #{limit} scrapes')
        rows = self._dal.query_recent_scrapes(limit)
        messages = []
        for r in rows:
            found = '🎉🎉🎉 FOUND 🎉🎉🎉 ' if r.is_found else 'nothing found'
            status = 'Error ❗ ' if r.is_error else 'Success run'
            since = humanfriendly.format_timespan(datetime.now(timezone.utc) - r.run_at, max_units=2)

            if not r.is_error:
                msg = f'{status} - {found} - {since} ago'
            else:
                msg = f'{status} - {found} - {r.error_message}: {r.error_details} - {since} ago'
            messages.append(msg)
        return '```\r\n{}```'.format('\r\n'.join(messages))

    def get_subscriptions(self) -> list[int]:
        self._logger.info('Querying subscriptions')
        rows = self._dal.query_subscriptions()

        return [r.chat_id for r in rows]

    def poll_storehouses(self) -> (bool, bool):
        is_found = False
        is_error = False
        error_message = None
        error_details = None

        try:
            self._logger.info('Querying storehouses page')
            response = self._pik_client.get_storehouse_page()
            paragraphs = parser.get_paragraphs(response)
            self._logger.info('Trying to find anything')
            is_found = not checker.check_storehouse_nothing_found_literal(paragraphs)
        except Exception as e:
            self._logger.exception('Failed scrape')
            is_error = True
            error_message = 'Exception occur during scrape'
            error_details = e
        self._dal.store_scrape(is_found, is_error, error_message, error_details)
        return is_found, is_error
