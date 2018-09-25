#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Union

from psycopg2 import IntegrityError
from psycopg2.extensions import connection

from model.entities import User


class MoneyAmountError(RuntimeError):
    pass


def create_db(conn: connection):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE SEQUENCE public.users_seq
            INCREMENT 1
            START 1
            MINVALUE 1
        """)
        cursor.execute("""
            CREATE TABLE USERS(
                id INTEGER PRIMARY KEY DEFAULT nextval('users_seq'::regclass),
                name VARCHAR NOT NULL UNIQUE,
                max_amount DECIMAL(10,2) NOT NULL,
                min_amount  DECIMAL(10,2) NOT NULL,
                current_amount DECIMAL(10,2) CHECK(current_amount >= min_amount AND current_amount <= max_amount)
            );
        """)


def drop_db(conn: connection):
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS USERS")
        cursor.execute("DROP SEQUENCE IF EXISTS public.users_seq")


def insert(conn: connection, user: User):
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO USERS (name, min_amount, max_amount, current_amount) VALUES (%s, %s, %s, %s) RETURNING id",
            [user.name, user.min_, user.max_, user.current]
        )
        user.id_ = cursor.fetchone()[0]


def get(conn: connection, name: str):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, min_amount, max_amount, current_amount FROM USERS WHERE name = %s",
            [name]
        )
        row = cursor.fetchone()
        if not row:
            return None
        user = User(id_=row[0], name=row[1], min_=row[2], max_=row[3], current=row[4])
        return user


def delete(conn: connection, id_: int):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM USERS WHERE id=%s", [id_])


def delete_by_name(conn: connection, name: str):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM USERS WHERE name=%s", [name])


def transfer_by_name(conn: connection, from_name: str, to_name: str, amount: Union[Decimal, int]):
    with conn.cursor() as cursor:
        try:
            cursor.execute("UPDATE USERS SET current_amount = current_amount - %s WHERE name=%s", [amount, from_name])
            cursor.execute("UPDATE USERS SET current_amount = current_amount + %s WHERE name=%s", [amount, to_name])
        except IntegrityError:
            raise MoneyAmountError()


def transfer_by_name_tpc(from_connection: connection, from_name: str, to_connection: connection, to_name: str,
                         amount: Union[Decimal, int]):
    with from_connection.cursor() as from_cursor, to_connection.cursor() as to_cursor:
        try:
            from_cursor.execute("UPDATE USERS SET current_amount = current_amount - %s WHERE name=%s",
                                [amount, from_name])
            to_cursor.execute("UPDATE USERS SET current_amount = current_amount + %s WHERE name=%s", [amount, to_name])
        except IntegrityError:
            raise MoneyAmountError()
