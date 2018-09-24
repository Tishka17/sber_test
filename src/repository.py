#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decimal import Decimal
from sqlite3 import Connection, register_adapter, register_converter
from typing import Union

from entities import User

register_adapter(Decimal, lambda d: str(d))
register_converter("decimal", lambda s: Decimal(s))


def create_db(connection: Connection):
    connection.execute("""
        CREATE TABLE USERS(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR NOT NULL UNIQUE,
            max DECIMAL(10,2) NOT NULL,
            min  DECIMAL(10,2) NOT NULL,
            current DECIMAL(10,2) CHECK(current >= min AND current <= max)
        );
    """)


def insert(connection: Connection, user: User):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO USERS (name, min, max, current) VALUES (?, ?, ?, ?)",
        [user.name, user.min_, user.max_, user.current]
    )
    user.id_ = cursor.lastrowid
    cursor.close()


def get(connection: Connection, name: str):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, name, min, max, current FROM USERS WHERE name = ?",
        [name]
    )
    row = cursor.fetchone()
    user = User(id_=row[0], name=row[1], min_=row[2], max_=row[3], current=row[4])
    cursor.close()
    return user


def delete(connection: Connection, id_: int):
    connection.execute("DELETE FROM USERS WHERE id=?", [id_])


def delete_by_name(connection: Connection, name: str):
    connection.execute("DELETE FROM USERS WHERE name=?", [name])


def transfer_by_name(connection: Connection, from_name: str, to_name: str, amount: Union[Decimal, int]):
    connection.execute("UPDATE USERS SET current=current-? WHERE name=?", [amount, from_name])
    connection.execute("UPDATE USERS SET current=current+? WHERE name=?", [amount, to_name])
