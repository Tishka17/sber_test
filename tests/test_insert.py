#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from psycopg2 import connect

from model.entities import User
from model.repository import drop_db, create_db, insert, get


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
