#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep

from repository import create_db, insert, transfer_by_name, get, MoneyAmountError, drop_db

from entities import User

from unittest import TestCase
from psycopg2 import connect
from threading import Thread, Lock, Condition


class TestInsert(TestCase):
    def setUp(self):
        self.connection = connect(dbname="tishka17")
        drop_db(self.connection)
        create_db(self.connection)
        self.connection.commit()

    def tearDown(self):
        drop_db(self.connection)
        self.connection.commit()
        self.connection.close()

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
        self.connection = connect(dbname="tishka17")
        drop_db(self.connection)
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

    def tearDown(self):
        drop_db(self.connection)
        self.connection.commit()
        self.connection.close()

    def test_transfer_ok(self):
        transfer_by_name(self.connection, self.name1, self.name2, 5)

        user1_after = get(self.connection, self.name1)
        user2_after = get(self.connection, self.name2)
        self.assertEqual(user1_after.current, 45)
        self.assertEqual(user2_after.current, 15)

    def test_transfer_not_enough(self):
        self.assertRaises(MoneyAmountError, transfer_by_name, self.connection, self.name2, self.name1, 15)
        self.connection.rollback()

    def test_tranfer_too_much(self):
        self.assertRaises(MoneyAmountError, transfer_by_name, self.connection, self.name1, self.name2, 20)
        self.connection.rollback()


class TestConcurrentTransfer(TestCase):
    name1 = "User1"
    name2 = "User2"

    def setUp(self):
        self.connection = connect(dbname="tishka17")
        drop_db(self.connection)
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
        self.connection2 = connect(dbname="tishka17")

    def concurrent_transfer(self):
        self.condition.acquire()
        while self.state != 1:
            self.condition.wait()
        self.condition.release()
        try:
            transfer_by_name(self.connection2, self.name2, self.name1, 10)
            self.connection2.commit()
        except MoneyAmountError:
            self.concurrent_failed = True

    def test_transfer_concurrent(self):
        self.condition = Condition()
        self.state = 0
        thread = Thread(target=lambda: self.concurrent_transfer())
        thread.start()
        transfer_by_name(self.connection, self.name2, self.name1, 10)

        self.state = 1
        self.condition.acquire()
        self.condition.notify_all()
        self.condition.release()
        sleep(0.1)
        self.connection.commit()
        thread.join()
        self.assertTrue(self.concurrent_failed)
