from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class BaseModel(DeclarativeBase):
    pass


class Token(BaseModel):
    __tablename__ = 'token'

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String())
    expires_in: Mapped[int] = mapped_column()

    def __repr__(self) -> str:
        return f'Token(id={self.id}, token={self.token[0:24]}, expires_in={self.expires_in})'


class Subscription(BaseModel):
    __tablename__ = 'subscription'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column()
    effective_user_name: Mapped[str] = mapped_column(String())

    def __repr__(self):
        return f'Subscription(id={self.id}, chat_id={self.chat_id}, effective_user_name={self.effective_user_name})'


class Scrape(BaseModel):
    __tablename__ = 'scrape'

    id: Mapped[int] = mapped_column(primary_key=True)
    is_found: Mapped[bool] = mapped_column(Boolean())
    is_error: Mapped[bool] = mapped_column(Boolean())
    error_message: Mapped[str] = mapped_column(String())
    error_details: Mapped[str] = mapped_column(String())
    run_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP())

    def __repr__(self):
        return (f'Scrape(id={self.id}, is_found={self.is_found}, is_error={self.is_error}, '
                f'error_message={self.error_message}, error_details={self.error_details}, '
                f'run_at={self.run_at})')
