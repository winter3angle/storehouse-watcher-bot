import os
from datetime import datetime

from sqlalchemy import create_engine, select, desc, delete
from sqlalchemy.orm import Session

from src.constants import envars
from src.dal.models import Token, Subscription, Scrape


class Dal:
    def __init__(self):
        conn_str = os.environ[envars.DB_CONN_STRING]
        if not conn_str:
            raise RuntimeError(f'{envars.DB_CONN_STRING} is not set')
        self._engine = create_engine(conn_str)

    def store_token(self, token: str, expires_in: int) -> None:
        with Session(self._engine) as sess:
            sess.add(Token(token=token, expires_in=expires_in))
            sess.commit()

    def query_recent_token(self) -> type(Token) | None:
        with Session(self._engine) as sess:
            statement = select(Token).order_by(desc(Token.id)).limit(1)
            return sess.scalar(statement)

    def try_store_subscription(self, chat_id: int, effective_user_name: str) -> int:
        query_subscription = select(Subscription).where(Subscription.chat_id == chat_id and
                                                        Subscription.effective_user_name == effective_user_name)
        with Session(self._engine) as sess:
            subscription = Subscription(chat_id=chat_id, effective_user_name=effective_user_name)
            with sess.begin():
                existing = sess.scalar(query_subscription)
                if existing:
                    return existing.id
                else:
                    sess.add(subscription)
            return subscription.id

    def delete_subscription(self, chat_id: int) -> None:
        with Session(self._engine) as sess:
            statement = delete(Subscription).where(Subscription.chat_id == chat_id)
            sess.execute(statement)
            sess.commit()

    def query_subscriptions(self) -> list[Subscription]:
        with Session(self._engine) as sess:
            statement = select(Subscription)
            result = sess.scalars(statement)
            return [r for r in result]

    def query_recent_scrapes(self, limit: int) -> list[Scrape]:
        with Session(self._engine) as sess:
            statement = select(Scrape).order_by(desc(Scrape.id)).limit(limit)
            result = sess.scalars(statement)
            sess.commit()

            return [r for r in result]

    def store_scrape(self, is_found: bool, is_error: bool,
                     error_message: str | None, error_details: str | None) -> None:
        with Session(self._engine) as sess:
            sess.add(Scrape(is_found=is_found, is_error=is_error, error_message=error_message,
                            error_details=error_details, run_at=datetime.utcnow()))
            sess.commit()
