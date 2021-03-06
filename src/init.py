#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from connect import connect_production

from model.use_cases import create_db

with connect_production() as conn:
    create_db(conn)
