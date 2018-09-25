#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from connect import connect

from model.repository import create_db

conn = connect()
create_db(conn)
conn.commit()
