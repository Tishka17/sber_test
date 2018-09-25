#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decimal import Decimal

from typing import Union

from model.entities import User
from psycopg2 import IntegrityError
from psycopg2.extensions import connection


class MoneyAmountError(RuntimeError):
    pass


def create_db(conn: connection):
    cursor = conn.cursor()
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
    cursor.close()


def drop_db(conn: connection):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS USERS")
    cursor.execute("DROP SEQUENCE IF EXISTS public.users_seq")
    cursor.close()


def insert(conn: connection, user: User):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO USERS (name, min_amount, max_amount, current_amount) VALUES (%s, %s, %s, %s) RETURNING id",
        [user.name, user.min_, user.max_, user.current]
    )
    user.id_ = cursor.fetchone()[0]
    cursor.close()


def get(conn: connection, name: str):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, min_amount, max_amount, current_amount FROM USERS WHERE name = %s",
        [name]
    )
    row = cursor.fetchone()
    user = User(id_=row[0], name=row[1], min_=row[2], max_=row[3], current=row[4])
    cursor.close()
    return user


def delete(conn: connection, id_: int):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM USERS WHERE id=%s", [id_])
    cursor.close()


def delete_by_name(conn: connection, name: str):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM USERS WHERE name=%s", [name])
    cursor.close()


def transfer_by_name(conn: connection, from_name: str, to_name: str, amount: Union[Decimal, int]):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE USERS SET current_amount = current_amount - %s WHERE name=%s", [amount, from_name])
        cursor.execute("UPDATE USERS SET current_amount = current_amount + %s WHERE name=%s", [amount, to_name])
    except IntegrityError as e:
        raise MoneyAmountError()
    cursor.close()
