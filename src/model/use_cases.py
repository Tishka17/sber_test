#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Union

from psycopg2 import Error
from psycopg2.extensions import connection

from .entities import User
from .repository import (
    transfer_by_name_tpc as transfer_by_name_tpc_impl,
    transfer_by_name as transfer_by_name_impl,
    insert as insert_impl,
    get as get_impl,
    create_db as create_db_impl,
    drop_db as drop_db_impl,
    MoneyAmountError
)


def create_db(conn: connection):
    create_db_impl(conn)
    conn.commit()


def drop_db(conn: connection):
    drop_db_impl(conn)
    conn.commit()


def get_user(conn: connection, name: str):
    return get_impl(conn, name)


def add_user(conn: connection, user: User):
    insert_impl(conn, user)
    conn.commit()
    return user


def transfer_by_name(conn: connection, from_name: str, to_name: str, amount: Union[Decimal, int]):
    try:
        transfer_by_name_impl(conn, from_name, to_name, amount)
        conn.commit()
    except MoneyAmountError:
        conn.rollback()
        raise


def transfer_by_name_tpc(from_connection: connection, from_name: str, to_connection: connection, to_name: str,
                         amount: Union[Decimal, int]):
    from_connection.tpc_begin(from_connection.xid(42, 'transaction ID', 'connection 1'))
    to_connection.tpc_begin(to_connection.xid(42, 'transaction ID', 'connection 2'))
    try:
        transfer_by_name_tpc_impl(from_connection, from_name, to_connection, to_name, amount)
        from_connection.tpc_prepare()
        to_connection.tpc_prepare()
    except Error:
        from_connection.tpc_rollback()
        to_connection.tpc_rollback()
        raise
    except MoneyAmountError:
        from_connection.tpc_rollback()
        to_connection.tpc_rollback()
        raise
    else:
        from_connection.tpc_commit()
        to_connection.tpc_commit()
