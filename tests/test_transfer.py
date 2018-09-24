#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from repository import create_db, insert, transfer_by_name, get, MoneyAmountError

from entities import User

from unittest import TestCase
from sqlite3 import connect


class TestInsert(TestCase):
    def setUp(self):
        self.connection = connect("TestInsert.db", isolation_level="EXCLUSIVE")
        create_db(self.connection)
        self.connection.commit()

    def tearDown(self):
        self.connection.close()
        os.unlink("TestInsert.db")

    def test_insert(self):
        user = User(
            name="User1",
            min_=0,
            max_=100,
            current=10
        )
        insert(self.connection, user)
        self.assertIsNotNone(user.id_)
        user2 = get(self.connection, user.name)
        self.assertEqual(user, user2)


class TestTransfer(TestCase):
    name1 = "User1"
    name2 = "User2"

    def setUp(self):
        self.connection = connect("TestTransfer.db", isolation_level="IMMEDIATE")
        create_db(self.connection)
        user = User(
            name=self.name1,
            min_=0,
            max_=100,
            current=50
        )
        insert(self.connection, user)
        user = User(
            name=self.name2,
            min_=0,
            max_=20,
            current=10
        )
        insert(self.connection, user)
        self.connection.commit()
        self.connection2 = connect("TestTransfer.db", isolation_level="IMMEDIATE")

    def tearDown(self):
        self.connection.close()
        self.connection2.close()
        os.unlink("TestTransfer.db")

    def test_transfer_ok(self):
        transfer_by_name(self.connection, self.name1, self.name2, 5)

        user1_after = get(self.connection, self.name1)
        user2_after = get(self.connection, self.name2)
        self.assertEqual(user1_after.current, 45)
        self.assertEqual(user2_after.current, 15)

    def test_transfer_not_enough(self):
        self.assertRaises(MoneyAmountError, transfer_by_name, self.connection, self.name1, self.name2, 20)
        self.connection.rollback()
        self.assertRaises(MoneyAmountError, transfer_by_name, self.connection, self.name2, self.name1, 15)
        self.connection.rollback()

    def test_transfer_concurrent(self):
        transfer_by_name(self.connection, self.name2, self.name1, 10)
        transfer_by_name(self.connection2, self.name2, self.name1, 10)
        self.connection.commit()
        self.connection2.commit()
