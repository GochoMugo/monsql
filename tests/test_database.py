import unittest
import sys
from datetime import *
import time
from base import *
from monsql import MonSQL, DESCENDING, DB_TYPES
from monsql.exception import MonSQLException

class MonSQLMetaOperationTest(BaseTestCase):
    
    def test_table_operations(self):
        tablename = 'test_table' + random_name()
        self.monsql.create_table(tablename, [('id INT NOT NULL')])
        self.assertTrue(self.monsql.is_table_existed(tablename))
        table_obj = self.monsql.get(tablename)

        for id in range(10):
            table_obj.insert({'id': id})
        self.monsql.commit()

        self.assertTrue(table_obj.count() == 10)
        for id in range(10):
            table_obj.insert({'id': id})

        self.assertEqual(table_obj.count(), 20)
        self.assertEqual(table_obj.count(distinct=True), 10)
        self.assertEqual(table_obj.count(query={'id': 2}), 2)
        self.assertEqual(table_obj.count(distinct=True, query={'id': 2}), 1)

        self.monsql.truncate_table(tablename)
        self.assertTrue(table_obj.count() == 0)

        is_exception_raised = False
        
        try:
            self.monsql.create_table(tablename, [('id INT')], force_recreate=False)
        except MonSQLException as e:
            is_exception_raised = True
        self.assertTrue(is_exception_raised)

        self.monsql.create_table(tablename, [('id INT')], primary_key=['id'], force_recreate=True)
        self.assertTrue(self.monsql.is_table_existed(tablename))

        self.monsql.drop_table(tablename)
        self.assertFalse(self.monsql.is_table_existed(tablename))