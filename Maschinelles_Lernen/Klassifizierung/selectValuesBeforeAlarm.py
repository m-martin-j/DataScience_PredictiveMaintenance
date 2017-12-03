import pyodbc
from datetime import datetime, timedelta

# connect to ms sql server
cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server=localhost;"
                      "Database=ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004;"
                      "Trusted_Connection=yes;")

cursor = cnxn.cursor()

# Select Alarmtimes
alarmTimes = cursor.execute("""SELECT StartDateTime FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[AlarmTimes]""").fetchall()


for entry in alarmTimes:
    #convert to datetime
    alarmTime = datetime.strptime(str(entry), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")

    #calculate relevant time period before alarm
    relevantPeriodStart = alarmTime - timedelta(days=3)

    #select values in relevant time period
    analogValues = cursor.execute(
        """SELECT AnalogSignalValues
            FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
                  
                  WHERE PK_Vehicle = 2 AND PK_DinGroup = 2035 AND StartDateTime >= ? and StartDateTime < ?""", (relevantPeriodStart, alarmTime)
    ).fetchall()


    #print results
    print("Values before " + str(alarmTime))
    for valueRow in analogValues: print(valueRow)
    print()