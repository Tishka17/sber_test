#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from connect import connect_production
from model import User
from model.use_cases import get_user

parser = ArgumentParser(description="Получение пользователя")
parser.add_argument("-n", "--name", required=True)

args = parser.parse_args()

with connect_production() as conn:
    user: User = get_user(conn, args.name)
    if not user:
        print("User with name `%s` not found" % args.name)
    else:
        print(user)
