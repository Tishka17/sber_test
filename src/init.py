#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from connect import connect

from repository import create_db

conn = connect()
create_db(conn)
