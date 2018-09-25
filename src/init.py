#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from connect import connect_production

from model.repository import create_db

conn = connect_production()
create_db(conn)
conn.commit()
