#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlite3 import connect as sqlite3_connect, Connection
from psycopg2 import connect as postgresql_connect


def connect() -> Connection:
    return postgresql_connect(dbname="tishka17")
