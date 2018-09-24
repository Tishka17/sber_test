#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlite3 import connect as sqlite3_connect, Connection


def connect() -> Connection:
    return sqlite3_connect("sample.db", isolation_level="EXCLUSIVE")
