import pyodbc

def connect_to_DB(servername, dbname):
    cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server="+servername+";"
                      "Database="+dbname+";"
                      "Trusted_Connection=yes;")
    try: # Check if connection good
        cursor = cnxn.cursor() # connection pointer
        print('Connection to MS SQL Server established\n--%--')
    except e: # RETRY
        print('Connection to MS SQL Server failed - retrying')
        if e.__class__ == pyodbc.ProgrammingError:
            cnxn == reinit()
            cursor = cnxn.cursor()

    return cursor
