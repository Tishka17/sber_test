#!/usr/bin/env python
# -*- coding: utf-8 -*-
from psycopg2 import connect as postgresql_connect
from psycopg2.extensions import connection


def connect() -> connection:
    return postgresql_connect(dbname="tishka17")
