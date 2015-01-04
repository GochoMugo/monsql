'''
Experimental use of a Language table to solve SQL variants.

See Discussion related to this: https://github.com/firstprayer/monsql/pull/10
Some research/must-read: https://www.udemy.com/blog/sql-queries/

Values preceded with ``$``, for example, $table_name, are placeholders in
the template strings. They are replaced with user-defined values when SQL
queries are built.
See https://docs.python.org/2/library/string.html#template-strings for more
information.

The used placeholders include (alphabetically ordered):

* column_name e.g. name
* columns e.g. name VARCHAR(50), age INTEGER
* discriminant e.g. WHERE age > 18
* table_name e.g. studentTable
* value e.g. 'gocho'
* values e.g. 'gocho', '19'

Redefining a query is allowed. The above placeholders may be placed
in the overriding query in with a ``$`` preceding them.
For example, in SQLite3, viewing tables requires such a query::

  sqlite3> SELECT name FROM sqlite_master WHERE type = 'table';

When building SQL queries, a **context** is used to derive such values.
A context is simply a dictionary-like object with keys matching the
placeholders in the strings. If a key is not found in the object, a
``MonSQLException`` is raised.
'''


from string import Template
from .exception import MonSQLException


common = {
  "create_table": Template("CREATE TABLE $table_name ($columns);"),
  "show_tables": Template("SHOW tables;"),
  "insert_record":Template("INSERT INTO $table_name ($columns) VALUES ($values);"),
  "view_record": Template("SELECT $columns FROM $table_name $discriminant;"),
  "delete_record": Template("DELETE FROM $table_name $discriminant;"),
  "update_record": Template("UPDATE $table_name SET $column_name = $value $discriminant;")
}


class SQL:
    def __init__(self, lang_dict=common):
        self.__lang_dict = lang_dict
        self.__context = None

    def define(self, dict_key, query):
        self.__lang_dict[dict_key] = Template(query)

    def build(self, dict_key, context=None):
        if context is not None:
            self.__context = context
        if self.__context is None:
            raise MonSQLException("Missing context")
        try:
            query = common.get(dict_key)
            return query.substitute(self.__context)
        except ValueError:
            raise MonSQLException("Missing template")
        except KeyError:
            raise MonSQLException("Missing parameter")
