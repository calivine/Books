from database.db import get_db

'''
    
    The Model class is meant to encapsulate 
    the functionality that goes into working
    with the database
    
'''


class Model(object):

    def __init__(self, user_id=''):
        self.user_id = user_id
        self.statement = ''
        self.arguments = []
        self.table = ''
        self.set_clause = ''
        self.predicate = ''
        self.command = ''
        self.db = get_db()

    # Table = table in database
    # Query = list of values to get from table
    # If table is empty, use query as the table variable and assume user wants all values from table
    # if table is only argument, use query position for table
    def select(self, *args):
        table = args[0]
        query = ', '.join(args[1:]) if len(args) > 1 else '*'
        command = 'SELECT '
        self.statement = command + query + " FROM " + table
        return self

    # "INSERT INTO activity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params
    # Takes table and list/tuple/dict of values to be inserted into table
    def insert(self, table, params):
        self.command = 'INSERT INTO '
        values = ",".join("?" * len(params))
        statement = self.command + table + " VALUES " + "(" + values + ")"
        self.db.execute(statement, params)
        self.db.commit()

    # 'UPDATE activity SET name = ? WHERE transaction_id = ?', (description, trans_id,)
    # SET name = description WHERE transaction_id = trans_id
    # Takes table and parameter to update
    # Chain to with() and save()
    def update(self, *args):
        self.table = args[0]
        self.command = 'UPDATE '
        self.set_clause = args[2]
        self.statement = self.command + self.table + ' SET ' + args[1] + ' = ?'
        return self

    # WHERE-method takes arguments:
    # arguments
    # conditions
    # which together form the predicate
    def where(self, *args):
        if len(args) == 1:
            self.arguments = args[0][2]
        else:
            for arg in args:
                self.arguments.append(arg[2])
        self.predicate = self._make_predicate(*args)
        return self

    # Build expression from table, query, and predicate
    # Takes list of variables as argument
    def get(self):
        self.arguments = (self.arguments, ) if type(self.arguments) is not list else self.arguments
        # statement = self._build()
        response = self.db.execute(self._build(), self.arguments).fetchall()
        self.arguments = []
        return list(map(dict, response))
        # return self._build()

    def save(self):
        # parameters = self.query + self.arguments
        # self.arguments.insert(0, self.set_clause)
        self.db.execute(self._build(), (self.set_clause, self.arguments,))
        self.db.commit()
        return self


    # Returns cols based on ID
    # Find( int/str: id )
    def find(self, id):
        print()

    @staticmethod
    def _make_predicate(*args):
        if len(args) == 1:
            return " WHERE " + str(args[0][0]) + " " + str(args[0][1]) + " ?"
        else:
            predicate = []
            for arg in args:
                predicate.append(str(arg[0]) + " " + str(arg[1]) + " ?")
            return " WHERE " + " AND ".join(predicate)

    def _build(self):
        return self.statement + self.predicate
