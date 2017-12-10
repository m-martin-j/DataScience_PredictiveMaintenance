import pyodbc
from datetime import datetime

# connect to ms sql server
cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server=localhost;"
                      "Database=ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004;"
                      "Trusted_Connection=yes;")

cursor = cnxn.cursor()
print("Connected!")

# Select all relevant values
print("loading all values...")
tableEntries = cursor.execute(
    """SELECT AnalogSignalValues, DateTime, PK_DinGroup
            FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
            WHERE PK_Vehicle = 2""").fetchall()

# Create new table
print("creating new table...")
cursor.execute("""CREATE TABLE [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[AnalogValues2] (
    PK_DinGroup smallint,
    DateTime datetime,
    AV1 integer,
    AV2 integer,
    AV3 integer,
    AV4 integer,
    AV5 integer,
    AV6 integer,
    AV7 integer,
    AV8 integer,
    AV9 integer
); """)
cnxn.commit()

# format and insert values
print("formatting values...")
for entry in tableEntries:
    timestamp = ""
    try:
        timestamp = datetime.strptime(str(entry[1]), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y%m%d %H:%M:%S")
    except:
        timestamp = datetime.strptime(str(entry[1]), "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d %H:%M:%S")

    formattedEntry = [entry[2], "'" + timestamp + "'"]

    values = entry[0].split(";", 9)
    del values[len(values)-1]
    for value in values:
        formattedEntry.append(int(value))

    cursor.execute("""INSERT INTO [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[AnalogValues2] VALUES (""" + ', '.join(str(x) for x in formattedEntry) + """)""")

cnxn.commit()