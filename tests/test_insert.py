#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from connect import connect_test

from model.entities import User
from model.use_cases import drop_db, create_db, add_user, get_user


class TestInsert(TestCase):
    def setUp(self):
        self.connection = connect_test()
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
        add_user(self.connection, user)
        self.assertIsNotNone(user.id_)
        user2 = get_user(self.connection, user.name)
        self.assertEqual(user, user2)
