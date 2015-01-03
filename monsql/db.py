#encoding=utf-8

"""
This is a module for using mysql as simple as using mongodb
Support mongodb manipulation like:

* find(queryObj, fieldObject)
* find_one(queryObj, fieldObject)
* insert(keyValueObj)
* insert_batch(a list of keyValueObj)
* update(queryObj, keyValueObj)
* remove(queryObj)

The design for this module would take **Pymongo** as a reference

Since it's a module for mysql, transaction must be considered, so we also provide:
* commit(): commit the transaction

We plan to Support Table join
We would also support subquery
"""

from config import TRANSACTION_MODE
from exception import MonSQLException
from table import Table


class Database:
    """
    MongoDB style of using MySQL

    :Examples:

    >>> monsql = MonSQL(host, port, username, password, dbname)
    >>> user_table = monsql.get('user')
    >>> activated_users = user_table.find({'state': 2})
    >>> user_ids = user_table.insert([{'username': ...}, {'username': ...}, ...])
    >>> user_table.commit() # OR monsql.commit()

    """

    def __init__(self, db, mode=TRANSACTION_MODE.DEFAULT):
        self.__db = db
        self.__cursor = self.__db.cursor()
        self.__table_map = {}
        self.__mode = mode

    def __ensure_table_obj(self, name):
        if not self.__table_map.has_key(name):
            self.__table_map[name] = self.__create_table_obj(name)

    def get(self, name):
        """
        Return a Table object to perform operations on this table. 

        Note that all tables returned by the samle MonSQL instance shared the same connection.

        :Parameters:

        - name: A table name

        :Returns: A Table object
        """
        self.__ensure_table_obj(name)
        return self.__table_map[name]

    def close(self):
        """
        Close the connection to the server
        """
        self.__db.close()
        self.__table_map = {}
        # self.__binded_map  = {}

    def commit(self):
        """
        Commit the current session
        """
        self.__db.commit()

    def __create_table_obj(self, name):
        table = Table(db=self.__db, name=name, mode=self.__mode)
        return table

    def set_foreign_key_check(self, to_check):
        """
        Enable/disable foreign key check. Disabling this is especially useful when
        deleting from a table with foreign key pointing to itself
        """
        if to_check:
            self.__db.cursor().execute('SET foreign_key_checks = 1;')
        else:
            self.__db.cursor().execute('SET foreign_key_checks = 0;')

    def is_table_existed(self, tablename):
        """
        Check whether the given table name exists in this database. Return boolean.
        """
        self.__cursor.execute('show tables')
        all_tablenames = [row[0].lower() for row in self.__cursor.fetchall()]
        tablename = tablename.lower()

        if tablename in all_tablenames:
            return True
        else:
            return False

    def create_table(self, tablename, columns, primary_key=None, force_recreate=False):
        """
        :Parameters:

        - tablename: string
        - columns: list or tuples, with each element be a string like 'id INT NOT NULL UNIQUE'
        - primary_key: list or tuples, with elements be the column names
        - force_recreate: When table of the same name already exists, if this is True, drop that table; if False, raise exception
        
        :Return: Nothing

        """
        if self.is_table_existed(tablename):
            if force_recreate:
                self.drop_table(tablename)
            else:
                raise MonSQLException('TABLE ALREADY EXISTS')

        columns_specs = ','.join(columns)
        if primary_key is not None:
            if len(primary_key) == 0:
                raise MonSQLException('PRIMARY KEY MUST AT LEAST CONTAINS ONE COLUMN')

            columns_specs += ',PRIMARY KEY(%s)' %(','.join(primary_key))

        sql = 'CREATE TABLE %s(%s)' %(tablename, columns_specs)
        self.__cursor.execute(sql)
        self.__db.commit()

    def drop_table(self, tablename, silent=False):
        """
        Drop a table

        :Parameters:

        - tablename: string
        - slient: boolean. If false and the table doesn't exists an exception will be raised;
          Otherwise it will be ignored
        
        :Return: Nothing

        """
        if not silent and not self.is_table_existed(tablename):
            raise MonSQLException('TABLE %s DOES NOT EXIST' %tablename)

        self.__cursor.execute('DROP TABLE IF EXISTS %s' %(tablename))
        self.__db.commit()

    def truncate_table(self, tablename):
        """
        Use 'TRUNCATE TABLE' to truncate the given table
        """
        self.__cursor.execute('TRUNCATE TABLE %s' %tablename)
        self.__db.commit()
