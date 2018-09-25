#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from connect import connect_test
from model.entities import User
from model.use_cases import transfer_by_name_tpc, drop_db, create_db, add_user, get_user, MoneyAmountError


class TestTpc(TestCase):
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
        self.connection2 = connect_test()

    def tearDown(self):
        self.connection.rollback()
        self.connection2.rollback()

        drop_db(self.connection)
        self.connection.commit()
        self.connection.close()
        self.connection2.close()

    def test_transfer_ok(self):
        transfer_by_name_tpc(self.connection, self.name1, self.connection2, self.name2, 5)

        user1_after = get_user(self.connection, self.name1)
        user2_after = get_user(self.connection2, self.name2)
        self.assertEqual(user1_after.current, 45)
        self.assertEqual(user2_after.current, 15)

    def test_transfer_not_enough(self):
        self.assertRaises(MoneyAmountError, transfer_by_name_tpc, self.connection, self.name2,
                          self.connection2, self.name1, 15)

        user1_after = get_user(self.connection, self.name1)
        user2_after = get_user(self.connection2, self.name2)
        self.assertEqual(user1_after.current, 50)
        self.assertEqual(user2_after.current, 10)
