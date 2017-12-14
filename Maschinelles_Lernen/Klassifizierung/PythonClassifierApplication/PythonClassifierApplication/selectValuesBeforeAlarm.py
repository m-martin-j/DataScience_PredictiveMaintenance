import pyodbc
from datetime import datetime, timedelta
import numpy as np
import sys
import math

#####################################
# Anleitung: Servername anpassen
SERVERNAME = "MJ-NOTEBOOK"
#####################################
"""
Sources:
SQL time formatting https://docs.microsoft.com/de-de/sql/t-sql/functions/cast-and-convert-transact-sql
"""

TIMEFRAME = 0.001 #days
TIMEFRAME_START = 3 #days prior event period starts ==> 3 days no_event values, 3 days event values, event point of time, relaxation time :: cycle restart
RELAXATION_TIME = 3 #hours
FRACTION_TRAIN = 0.75 # fraction of exapmles that will be train data (1-fraction is test data)

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
eventTimes = cursor.execute("""SELECT DISTINCT StartDateTime FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[AlarmTimes]
    ORDER BY StartDateTime ASC""").fetchall()
# TODO: DANIEL: AlarmTimes Tabelle hat jeden Zeitpunkt doppelt
tfirst_event = datetime.strptime( str(eventTimes[0]), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")
tlast_event = datetime.strptime( str(eventTimes[-1]), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")
print('SVM on Concerto Data\n\nfirst event date ',tfirst_event)
print('last event date ',tlast_event)

# let training data start k days prior to first event date (contains no_event and event values)
tno_event_start = tfirst_event - timedelta (days=TIMEFRAME) - timedelta(days=TIMEFRAME_START)
print('Training data starting at ', tno_event_start)
print('-------------------------------')
###########################


# grab values
display_count = 0 # for progress information in console
teventTime_prior = 0
# create lists
event_values = []
no_event_values = []
labels = []

for entry in eventTimes:
    #convert to datetime
    teventTime = datetime.strptime( str(entry), "(datetime.datetime(%Y, %m, %d, %H, %M, %S, %f), )")

    #calculate relevant time period before alarm
    trelevantPeriodStart = teventTime - timedelta(days=TIMEFRAME)

    search_no_events = True
    if tno_event_start >= trelevantPeriodStart:
        search_no_events = False
        trelevantPeriodStart = teventTime_prior
    
    if search_no_events:
        #select values in no_event time period till start of next relevant time period -> LABEL = 0
        # TODO: evtl leere Abfragen regeln
        no_event_vals = cursor.execute(SQL_PART_ROUTINE+"WHERE PK_Vehicle = 2 AND PK_DinGroup = 2035 AND StartDateTime >= ? and StartDateTime < ?", (tno_event_start,trelevantPeriodStart)
        ).fetchall()

    #select values in relevant event time period -> LABEL = 1
    # TODO: evtl leere Abfragen regeln
    event_vals = cursor.execute(SQL_PART_ROUTINE+"WHERE PK_Vehicle = 2 AND PK_DinGroup = 2035 AND StartDateTime >= ? and StartDateTime < ?", (trelevantPeriodStart, teventTime)
    ).fetchall()



    # update start time of no_event values (just after last alarm)
    # TODO: Kollisionen mit bereits neu startendem Event regeln
    tno_event_start = teventTime + timedelta(hours=RELAXATION_TIME)
    teventTime_prior = teventTime

    # append new values and set labels
    if search_no_events:
        for row in no_event_vals:
            no_event_values.append([ *( float(i) for i in row[0].split(';')[:8] ) ]) # only take the first 8 columns of ASV string
    for row in event_vals:
        event_values.append([ *( float(i) for i in row[0].split(';')[:8] ) ])

    # show progress in console
    if search_no_events:
        display_count += len(no_event_vals)+len(event_vals)
    else:
        display_count += len(event_vals)
    sys.stdout.write("\r#ASV tupels collected: %i" % display_count)
    sys.stdout.flush()
print("\n")
###########################


# make data array and set labels
nbr_train_data_event = math.ceil( len(event_values)*FRACTION_TRAIN ) 
data_train = np.array( event_values[:nbr_train_data_event] )
print("Laenge data_train mit event =", len(data_train) )
labels_train = np.ones(nbr_train_data_event)
print("Laenge labels_train mit event =", len(labels_train) )
nbr_train_data_no_event = math.ceil( len(no_event_values)*FRACTION_TRAIN ) 
data_train = np.append( data_train, no_event_values[:nbr_train_data_no_event], axis = 0 )
print("Laenge data_train mit event + ohne event =", len(data_train) )
labels_train = np.append( labels_train, np.zeros(nbr_train_data_no_event), axis = 0 )
print("Laenge labels_train mit event + ohne event =", len(labels_train) )

data_test = np.array( event_values[nbr_train_data_event:] )
print("Laenge data_test mit event =", len(data_test) )
labels_test = np.ones(len(event_values) - nbr_train_data_event)
print("Laenge labels_test mit event =", len(labels_test) )
data_test = np.append( data_test, no_event_values[nbr_train_data_no_event:], axis = 0 )
print("Laenge data_test mit event + ohne event =", len(data_test) )
labels_test = np.append( labels_test, np.zeros(len(no_event_values)-nbr_train_data_no_event), axis = 0 ) 
print("Laenge labels_test mit event + ohne event =", len(labels_test) )

print("\n\nNumber of data_train with event + no_event =", len(data_train))
print("Number of labels_train = %s (1:%s, 0:%s)" % (len(labels_train), np.count_nonzero(labels_train), len(labels_train)-np.count_nonzero(labels_train)) )
print("Number of data_test with event + no_event =", len(data_test))
print("Number of labels_test = %s (1:%s, 0:%s)" % (len(labels_test), np.count_nonzero(labels_test), len(labels_test)-np.count_nonzero(labels_test)) )
print('-------------------------------')



####################################################################
# SVM
from sklearn.svm import SVC
from sklearn import metrics


lin_classifier = SVC()
lin_classifier.fit(data_train, labels_train)
a = lin_classifier.predict(data_test)
cfm1 = metrics.confusion_matrix(labels_test, a)

#True negative
tn = cfm1[0][0]
#False positive
fp = cfm1[0][1]
#False negative
fn = cfm1[1][0] 
#True positive
tp = cfm1[1][1]

print(cfm1)

genauigkeit = lin_classifier.score(data_test, labels_test) 
print('Genauigkeit: ', genauigkeit)
tpr = tp/(tp+fn)
print('truepositiverate:', tpr)
fpr = fp/(fp+tn)
print('falsepositiverate:', fpr)
klassifikationsfehler = (fp + fn)/(tp+fp+tn+fn)
print('Klassifikationsfehler: ', klassifikationsfehler)
guete = (tp + tn)/(tp+fp+tn+fn)
print('Güte: ', guete, "\n")