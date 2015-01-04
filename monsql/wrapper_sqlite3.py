'''
SQLite3
-------
A lightweight disk-based database. Usually useful for internal
data storage and prototyping for applications.
'''


import sqlite3
from db import Database
from lang import SQL
from table import Table

class SQLite3Table(Table):
    def fetch_columns(self):
        sql = u"PRAGMA table_info(%s)" %(self.name)
        self.cursor.execute(sql)
        columns = []

        for column in self.cursor.fetchall():
            column = column[1]
            columns.append(column)
        self.columns = columns


sqlite3Lang = SQL()
sqlite3Lang.define("show_tables", "SELECT name FROM sqlite_master WHERE type = 'table' ")


class SQLite3(Database):
    def __init__(self, file_path=None):
        if file_path is None: file_path = ":memory:"
        db = sqlite3.connect(file_path)
        Database.__init__(self, db, language=sqlite3Lang)

    def get_table_obj(self, name):
        table = SQLite3Table(db=self.db, name=name, mode=self.mode)
        return table

    def truncate_table(self, tablename):
        """
        SQLite3 doesn't support direct truncate, so we just use delete here
        """
        self.get(tablename).remove()
        self.db.commit()

        
