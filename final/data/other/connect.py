import pymysql

class connector:
    def __init__(self):
        # Open database connection
        self.db = pymysql.connect("localhost","amy","fighting","md" )

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor()

        # execute SQL query using execute() method.
        self.cursor.execute("SELECT VERSION()")

        # Fetch a single row using fetchone() method.
        data = self.cursor.fetchone()
        print ("Database version : %s " % data)

    def execute(self, query):
        try:
            self.cursor.execute(query)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

        return self.cursor.fetchall()

    def __del__(self):
        # disconnect from server
        self.db.close()

    def __exit__(self):
        # disconnect from server
        self.db.close()

