#encoding=utf-8

import abc
from config import TRANSACTION_MODE
from exception import MonSQLException
from queryset import DataRow
from table import Table


class Database:
    """
    Database wrapper for interaction with specific database
    """
    def __init__(self, db, language, mode=TRANSACTION_MODE.DEFAULT):
        self.__db = db
        self.__cursor = self.__db.cursor()
        self.__language = language
        self.__table_map = {}
        self.__mode = mode

    """
    Properties for accessibility to subclasses
    """
    @property
    def cursor(self):
        return self.__cursor

    @property
    def db(self):
        return self.__db

    @property
    def mode(self):
        return self.__mode

    def __ensure_table_obj(self, name):
        if not self.__table_map.has_key(name):
            self.__table_map[name] = self.get_table_obj(name)

    def get_table_obj(self, name):
        table = Table(self.db, name, self.__language, mode=self.mode)
        return table

    def list_tables(self):
        """
        Return a list of lower case table names. Different databases have their own ways to 
        do this, so leave the implementation to the subclasses
        """
        self.cursor.execute(self.__language.build("show_tables", context={}))
        all_tablenames = [row[0].lower() for row in self.cursor.fetchall()]
        return all_tablenames

    def truncate_table(self, tablename):
        """
        Use 'TRUNCATE TABLE' to truncate the given table
        """
        self.cursor.execute(self.__language.build("truncate_table", {table_name: tablename}))
        self.db.commit()

    def get(self, name):
        """
        Return a Table object to perform operations on this table. 

        Note that all tables returned by the samle Database instance shared the same connection.

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

    def commit(self):
        """
        Commit the current session
        """
        self.__db.commit()
    
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
        all_tablenames = self.list_tables()
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

        sql = self.__language.build("create_table", table_name=tablename, columns=columns_specs)
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

        sql = self.__language.build("drop_table", table_name=tablename, if_exists="IF EXISTS")
        self.__cursor.execute(sql)
        self.__db.commit()

    def raw(self, sql):
        """
        Execute raw sql
        :Parameters:

        - sql: string, sql to be executed

        :Return: the result of this execution

        If it's a select, return a list with each element be a DataRow instance

        Otherwise return raw result from the cursor (Should be insert or update or delete)

        """
        res = self.cursor.execute(sql)
        if self.cursor.description is None:
            return res

        rows = self.cursor.fetchall()
        columns = [d[0] for d in self.cursor.description]

        structured_rows = []
        for row in rows:
            data = {}
            for val, col in zip(row, columns):
                data[col] = val
            structured_rows.append(DataRow(data))

        return structured_rows
