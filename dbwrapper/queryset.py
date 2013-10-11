
from query import Query
from sql import build_select

"""
Lazy load data
"""
class QuerySet:

    def __init__(self, cursor, query):
        self.cursor = cursor
        self.query = query
        self._data = None
        self._need_to_refetch_data = False

    """
    Python magic functions
    """
    def __len__(self):
        if not self._data or self._need_to_refetch_data:
            self._fetch_data()
        return len(self._data)

    def __iter__(self):
        if not self._data or self._need_to_refetch_data:
            self._fetch_data()
        return iter(self._data)

    def __getitem__(self, k):
        if not self._data or self._need_to_refetch_data:
            self._fetch_data()
        return self._data[k]

    def _fetch_data(self):
        print "fetching data"
        sql = build_select(self.query)
        self.cursor.execute(sql)
        # Wrap the data into dictionaries
        data_list = self.cursor.fetchall()
        values = self.query.fields
        result_list = []
        for data in data_list:
            assert(len(data) == len(values))
            result = {}
            for i in range(len(data)):
                result[values[i]] = data[i]
            result_list.append(result)

        self._data = result_list
        self._need_to_refetch_data = False

    def filter(self, filter):
        self._need_to_refetch_data = True
        pass

    def sort(self, sort):
        self._need_to_refetch_data = True
        pass
