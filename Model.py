from database.db import get_db

'''
    
    The Model class is meant to encapsulate 
    the functionality that goes into working
    with the database
    
'''


class Model(object):

    # Initialize DB



    def __init__(self, user_id):
        self.user_id = user_id
        self.conditions = ''
        self.arguments = ''
        self.table = ''
        self.query = ''
        self.predicate = ''
        self.command = ''
        self.db = get_db()

    # WHERE-method takes arguments:
    # arguments
    # conditions
    # which together form the predicate
    def where(self, arguments, conditions=None):
        self.conditions = conditions
        self.arguments = arguments

        print(self.conditions)
        print(self.arguments)
        print(type(self.conditions))
        print(type(self.arguments))

        # Standardize lists
        self._return_lists()

        # Build predicate
        self.predicate = self._predicate()

        return self

    # Table = table in database
    # Query = list of values to get from table
    # If table is empty, use query as the table variable and assume user wants all values from table
    # if table is only argument, use query position for table
    def select(self, query, table=None):
        self.query = query
        self.table = table if table is not None else query
        self.command = 'SELECT'
        return self

    # "INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params
    # Takes table and list/tuple/dict of values to be inserted into table
    def insert(self, table, params):
        self.command = 'INSERT INTO '
        values = ",".join("?" * len(params))
        statement = self.command + table + " VALUES " + "(" + values + ")"
        self.db.execute(statement, params)
        self.db.commit()

    # Build expression from table, query, and predicate
    # Takes list of variables as argument
    def get(self, data=''):
        response = self.db.execute(self._build(), data).fetchall()
        return list(map(dict, response))
        # return self._build()

    # Standardize lists for building predicate
    def _return_lists(self):
        if self.conditions is None or (type(self.conditions) is str and type(self.arguments) is str):
            return self
        # If both arguments are strings, it is a single argument query
        # elif type(self.conditions) is str and type(self.arguments) is str:
        #     return self
        # If first argument is string and second is a list, it is a query based on a range of values
        elif type(self.conditions) is str and type(self.arguments) is list:
            condition = self.conditions
            self.conditions = []
            for i in range(len(self.arguments)):
                self.conditions = self.conditions + [condition]
        elif len(self.conditions) > len(self.arguments):
            for i in range(len(self.conditions)):
                if i >= len(self.arguments):
                    self.arguments = self.arguments + [self.arguments[len(self.arguments) - 1]]  # Repeat last item of arguments list
        else:
            return self
        return self

    def _predicate(self):
        predicate = []
        # Create list of comparison operators that make up the predicate in the form:
        # 'arg1 cond1 ?' could translate to 'id = ?' where arg1 = 'id', cond1 = '='
        if self.conditions is None:
            for i in range(len(self.arguments)):
                predicate.append(str(self.arguments[i]) + " = ?")
        else:
            for i in range(len(self.arguments)):
                predicate.append(str(self.arguments[i]) + " " + self.conditions[i] + " ?")
        predicate = " AND ".join(predicate) if len(predicate) > 1 else predicate
        return " WHERE " + predicate

    def _build(self):
        if self.query is self.table:
            response = self.command + " * FROM " + self.query + self.predicate
        else:
            query_list = self.query
            self.query = ", ".join(query_list) if type(query_list) is list else query_list
            response = self.command + " " + self.query + " FROM " + self.table + self.predicate
        # Reset values
        self.predicate = ''
        self.query = ''
        self.table = ''
        return response
