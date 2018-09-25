#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from decimal import Decimal
from connect import connect

from model.repository import transfer_by_name, get

parser = ArgumentParser()
parser.add_argument("-f", "--from", dest="from_", type=str)
parser.add_argument("-t", "--to", dest="to_", type=str)
parser.add_argument("amount", type=Decimal)

args = parser.parse_args()

conn = connect()
print("--- BEFORE TRANSFER ---")
print(get(conn, args.from_))
print(get(conn, args.to_))
transfer_by_name(conn, args.from_, args.to_, args.amount)
print()
print("--- AFTER TRANSFER ---")
print(get(conn, args.from_))
print(get(conn, args.to_))
conn.commit()
