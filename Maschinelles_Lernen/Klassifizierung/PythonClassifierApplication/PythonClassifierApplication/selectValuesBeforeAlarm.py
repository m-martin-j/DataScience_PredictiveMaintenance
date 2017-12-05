import pyodbc
from datetime import datetime, timedelta
import numpy as np
import sys

##############################
## Anleitung: Servername ändern
SERVERNAME = "MJ-NOTEBOOK"
##############################


TIMEFRAME = 3 #days
TIMEFRAME_START = 7 #days
RELAXATION_TIME = 3 #hours
SQL_PART_ROUTINE =  """SELECT AnalogSignalValues
            FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
                    """


# connect to ms sql server
cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server="+SERVERNAME+";"
                      "Database=ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004;"
                      "Trusted_Connection=yes;")

cursor = cnxn.cursor()
###########################


# Select event times (Alarm, Warnungen), predefined as table in MS SQL server
eventTimes = cursor.execute("""SELECT StartDateTime FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[AlarmTimes]
    ORDER BY StartDateTime ASC""").fetchall()
tfirst_event = datetime.strptime( str(eventTimes[0]), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")
tlast_event = datetime.strptime( str(eventTimes[-1]), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")
print('first event date ',tfirst_event)
print('last event date ',tlast_event)

# let training data start k days prior to first event date (contains no_event and event values)
tvalues_start = tfirst_event - timedelta(days=TIMEFRAME_START)
print('Training data starting at ', tvalues_start)
print('-------------------------------')
###########################


# grab values
# no_event values between the respective time frames shall be incorporated
tno_event_start = tvalues_start
display_count = 0 # for progress information in console
# create lists
event_values = []
no_event_values = []
labels = []

for entry in eventTimes:
    #convert to datetime
    teventTime = datetime.strptime( str(entry), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")

    #calculate relevant time period before alarm
    trelevantPeriodStart = teventTime - timedelta(days=TIMEFRAME)

    #select values in no_event time period till start of next relevant time period -> LABEL = 0
    # TODO: leere Abfragen regeln
    no_event_vals = cursor.execute(SQL_PART_ROUTINE+"WHERE PK_Vehicle = 2 AND PK_DinGroup = 2035 AND StartDateTime >= ? and StartDateTime < ?", (tno_event_start,trelevantPeriodStart)
    ).fetchall()


    #select values in relevant event time period -> LABEL = 1
    # TODO: leere Abfragen regeln
    event_vals = cursor.execute(SQL_PART_ROUTINE+"WHERE PK_Vehicle = 2 AND PK_DinGroup = 2035 AND StartDateTime >= ? and StartDateTime < ?", (trelevantPeriodStart, teventTime)
    ).fetchall()

    # update start time of no_event values (just after last alarm)
    # TODO: Kollisionen mit bereits neu startendem Event regeln
    tno_event_start = teventTime + timedelta(hours=RELAXATION_TIME)


    # append new values and set labels
    for row in no_event_vals:
        no_event_values.append([ *( float(i) for i in row[0].split(';')[:8] ) ]) # only take the first 8 columns of ASV string
    for row in event_vals:
        event_values.append([ *( float(i) for i in row[0].split(';')[:8] ) ])

    # show progress in console
    display_count += len(no_event_vals)+len(event_vals)
    sys.stdout.write("\rASV tupels collected: %i" % display_count)
    sys.stdout.flush()

###########################


# make data array and set labels
data = np.array(event_values)
data = np.append(data,no_event_values, axis= 0)

labels = np.ones((len(event_values),1))
temp1 = np.zeros((len(no_event_values),1))
labels = np.append(labels,temp1,axis= 0)


#print results
#print("Values before " + str(alarmTime))
#for valueRow in analogValues: print(valueRow)
#print()

