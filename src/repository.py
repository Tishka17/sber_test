#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decimal import Decimal

from typing import Union

from entities import User
from psycopg2 import IntegrityError


class MoneyAmountError(RuntimeError):
    pass


def create_db(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE SEQUENCE public.your_sequence
        INCREMENT 1
        START 1
        MINVALUE 1
    """)
    cursor.execute("""
        CREATE TABLE USERS(
            id INTEGER PRIMARY KEY DEFAULT nextval('your_sequence'::regclass),
            name VARCHAR NOT NULL UNIQUE,
            max DECIMAL(10,2) NOT NULL,
            min  DECIMAL(10,2) NOT NULL,
            current DECIMAL(10,2) CHECK(current >= min AND current <= max)
        );
    """)
    cursor.close()


def drop_db(connection):
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS USERS")
    cursor.execute("DROP SEQUENCE IF EXISTS public.your_sequence")
    cursor.close()


def insert(connection, user: User):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO USERS (name, min, max, current) VALUES (%s, %s, %s, %s) RETURNING id",
        [user.name, user.min_, user.max_, user.current]
    )
    user.id_ = cursor.fetchone()[0]
    cursor.close()


def get(connection, name: str):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, name, min, max, current FROM USERS WHERE name = %s",
        [name]
    )
    row = cursor.fetchone()
    user = User(id_=row[0], name=row[1], min_=row[2], max_=row[3], current=row[4])
    cursor.close()
    return user


def delete(connection, id_: int):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM USERS WHERE id=%s", [id_])
    cursor.close()


def delete_by_name(connection, name: str):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM USERS WHERE name=%s", [name])
    cursor.close()


def transfer_by_name(connection, from_name: str, to_name: str, amount: Union[Decimal, int]):
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE USERS SET current=current-%s WHERE name=%s", [amount, from_name])
        cursor.execute("UPDATE USERS SET current=current+%s WHERE name=%s", [amount, to_name])
    except IntegrityError as e:
        raise MoneyAmountError()
    cursor.close()
