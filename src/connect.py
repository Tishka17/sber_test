#!/usr/bin/env python
# -*- coding: utf-8 -*-
from psycopg2 import connect as postgresql_connect
from psycopg2.extensions import connection
import yaml


def connect_production() -> connection:
    with open("production.yml", "r", encoding="utf-8") as f:
        config = yaml.load(f)
    return postgresql_connect(**config)


def connect_test() -> connection:
    with open("test.yml", "r", encoding="utf-8") as f:
        config = yaml.load(f)
    return postgresql_connect(**config)
