"""create subscriptions table

Revision ID: 1e1de6332785
Revises: 631d149bda68
Create Date: 2023-09-15 23:12:29.593508

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1e1de6332785'
down_revision: Union[str, None] = '631d149bda68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql = '''
    create table "subscription" (
        id                  bigserial primary key not null,
        chat_id             bigint not null,
        effective_user_name text not null,
        constraint uq_subscription_chat_id unique (chat_id)
    )
    '''
    op.execute(sql)


def downgrade() -> None:
    sql = '''
    drop table if exists "subscription"
    '''
    op.execute(sql)
