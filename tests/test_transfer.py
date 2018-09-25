#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread, Condition
from time import sleep
from unittest import TestCase

from connect import connect_test
from model.entities import User
from model.use_cases import create_db, add_user, get_user, MoneyAmountError, drop_db
from model.repository import transfer_by_name


class TestTransfer(TestCase):
    name1 = "User1"
    name2 = "User2"

    def setUp(self):
        self.connection = connect_test()
        drop_db(self.connection)
        create_db(self.connection)
        user = User(
            name=self.name1,
            min_=0,
            max_=100,
            current=50
        )
        add_user(self.connection, user)
        user = User(
            name=self.name2,
            min_=0,
            max_=20,
            current=10
        )
        add_user(self.connection, user)
        self.connection.commit()

    def tearDown(self):
        drop_db(self.connection)
        self.connection.commit()
        self.connection.close()

    def test_transfer_ok(self):
        transfer_by_name(self.connection, self.name1, self.name2, 5)

        user1_after = get_user(self.connection, self.name1)
        user2_after = get_user(self.connection, self.name2)
        self.assertEqual(user1_after.current, 45)
        self.assertEqual(user2_after.current, 15)

    def test_transfer_not_enough(self):
        self.assertRaises(MoneyAmountError, transfer_by_name, self.connection, self.name2, self.name1, 15)
        self.connection.rollback()

    def test_transfer_too_much(self):
        self.assertRaises(MoneyAmountError, transfer_by_name, self.connection, self.name1, self.name2, 20)
        self.connection.rollback()


class TestConcurrentTransfer(TestCase):
    name1 = "User1"
    name2 = "User2"

    def setUp(self):
        self.connection = connect_test()
        drop_db(self.connection)
        create_db(self.connection)
        user = User(
            name=self.name1,
            min_=0,
            max_=100,
            current=50
        )
        add_user(self.connection, user)
        user = User(
            name=self.name2,
            min_=0,
            max_=20,
            current=10
        )
        add_user(self.connection, user)
        self.connection2 = connect_test()

    def tearDown(self):
        drop_db(self.connection)
        self.connection.close()
        self.connection2.close()

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
