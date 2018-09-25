#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from decimal import Decimal

from connect import connect_production
from model import MoneyAmountError
from model.use_cases import transfer_by_name, get_user

parser = ArgumentParser(description="Перевод денег между двемя пользователями")
parser.add_argument("-f", "--from", dest="from_", type=str)
parser.add_argument("-t", "--to", dest="to_", type=str)
parser.add_argument("amount", type=Decimal)

args = parser.parse_args()

with connect_production() as conn:
    print("--- BEFORE TRANSFER ---")
    print(get_user(conn, args.from_))
    print(get_user(conn, args.to_))
    print()

    try:
        transfer_by_name(conn, args.from_, args.to_, args.amount)
        print("Money transfer is successful")
    except MoneyAmountError:
        print("Invalid money amount. Check limits")

    print()
    print("--- AFTER TRANSFER ---")
    print(get_user(conn, args.from_))
    print(get_user(conn, args.to_))
    conn.commit()
