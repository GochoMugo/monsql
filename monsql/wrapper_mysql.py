'''
MySQL
--------
The World's "most" popular open source database
'''


import MySQLdb
import sqlstr
from db import Database
from table import Table
from config import TRANSACTION_MODE


class MySQL(Database):

    def __init__(self, host='127.0.0.1', port=3306, username='', password='',
                 dbname='test', mode=TRANSACTION_MODE.DEFAULT):
        db = MySQLdb.Connect(host=host, port=port, user=username,
                                    passwd=password, db=dbname)
        Database.__init__(self, db, language=sqlstr.MySQL())
