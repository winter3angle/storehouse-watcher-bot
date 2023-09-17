"""create token table

Revision ID: 631d149bda68
Revises: 
Create Date: 2023-09-03 21:41:15.369722

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '631d149bda68'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql = '''
    create table "token" (
        id         bigserial primary key not null,
        token      text                  not null,
        expires_in bigint                not null
    )
    '''
    op.execute(sql)


def downgrade() -> None:
    sql = '''
    drop table if exists "token";
    '''
    op.execute(sql)
