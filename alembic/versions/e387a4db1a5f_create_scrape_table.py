"""create scrape table

Revision ID: e387a4db1a5f
Revises: 1e1de6332785
Create Date: 2023-09-15 23:25:21.464931

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e387a4db1a5f'
down_revision: Union[str, None] = '1e1de6332785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql = '''
    create table "scrape" (
        id            bigserial primary key not null,
        is_found      boolean not null,
        is_error      boolean not null,
        error_message text,
        error_details text,
        run_at        timestamp with time zone not null default now()
    )
    '''
    op.execute(sql)


def downgrade() -> None:
    sql = '''
    drop table if exists "scrape"
    '''
    op.execute(sql)
