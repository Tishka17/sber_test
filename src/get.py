#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from model.entities import User
from model.repository import get
from connect import connect_production

parser = ArgumentParser(description="Получение пользователя")
parser.add_argument("-n", "--name", required=True)

args = parser.parse_args()

with connect_production() as conn:
    user = get(conn, args.name)
    if not user:
        print("User with name `%s` not found" % args.name)
    else:
        print(user)