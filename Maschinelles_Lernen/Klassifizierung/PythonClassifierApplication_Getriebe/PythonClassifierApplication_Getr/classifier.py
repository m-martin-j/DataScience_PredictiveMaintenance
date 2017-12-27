import sys
from datetime import datetime, timedelta
import pyodbc
import numpy as np
import math


"""
Sources:
SQL time formatting https://docs.microsoft.com/de-de/sql/t-sql/functions/cast-and-convert-transact-sql
"""

##################################### Global Variables
SERVERNAME = 'localhost'
VEHICLE_NUMBER = '2' 
DEFINITIONNUMBER_EVENT = '41' # consult SQL-query "see_DefinitionNumber_and_respective_DinGroup" to find the correct DefinitionNumber
DEFINITIONNUMBER_ASV = '6'
NUMBER_ASV_POSITIONS = 7 # only the first NUMBER_ASV_POSITIONS positions of ASV string are relevant
START_EVENTS_FORMATTED = datetime.strptime( '2017-01-17', "%Y-%m-%d") # point of time of very first event AND event ASV
TIMEFRAME_EVENT_ASV = 3*24 # hours
TIME_AFTER_LAST_EVENT = 10*24 # hours (no_event values start at that point of time)
TIMEFRAME_NO_EVENT_ASV = 6*24 # hours 

FRACTION_TRAIN = 0.7 # fraction of exapmles that will be train data (1-fraction is test data)


# following SQL queries execute relevant joins w/o SELECT statement
SQL_PART_ROUTINE =  """FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
                  WHERE ReadOut.FK_Vehicle = """+VEHICLE_NUMBER
#####################################

print('-----------------------\nSVM on Concerto Data\n-----------------------')



##################################### connect to ms sql server
cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server="+SERVERNAME+";"
                      "Database=ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004;" #TIF Database
                      "Trusted_Connection=yes;")
try: # Check if connection good
    cursor = cnxn.cursor() # connection pointer
    print('Connection to MS SQL Server established\n--%--')
except e: # RETRY
    print('Connection to MS SQL Server failed - retrying')
    if e.__class__ == pyodbc.ProgrammingError:        
        cnxn == reinit()
        cursor = cnxn.cursor()
#####################################


##################################### grab and format event time stamps
event_times_unformatted = cursor.execute("""SELECT StartDateTime """+SQL_PART_ROUTINE+
                                        """ AND TriggerSignalValue = 1  -- otherwise each alarm time is selected twice
                                        AND DiagnosticDataSetDefinition.DefinitionNumber = """+DEFINITIONNUMBER_EVENT+"""
                                        AND StartDateTime >= ?   
                                        ORDER BY StartDateTime ASC""", (START_EVENTS_FORMATTED)
                                        ).fetchall()
print('Event time stamps collected\n--%--')
event_times = []
for row in event_times_unformatted:
    event_times.append(row[0])
n_event_times = len(event_times)
event_time_first = event_times[0]
event_time_last = event_times[-1]
event_time_diff = event_time_last - event_time_first # time difference between first and last alarm
print('Event time stamps formatted')
print('Number of events: %s,\nranging from %s to %s (%s)' % (n_event_times, event_times[0].strftime('%Y/%m/%d %H:%M'), event_times[-1].strftime('%Y/%m/%d %H:%M'), event_time_diff) )
print('--%--')
#####################################


##################################### grab event AnalogSignalValues
print('start collecting event ASV')
prior_event_time = 0
event_ASV = [] # array containing event ASV tupels
display_count = 0 # counter for command line output

for event_time in event_times:
    # calculate relevant time period before event
    relevant_period_start = event_time - timedelta(hours=TIMEFRAME_EVENT_ASV)
    if prior_event_time != 0 and prior_event_time >= relevant_period_start: # less than TIMEFRAME_EVENT_ASV hours between two events
        relevant_period_start = prior_event_time

    if relevant_period_start < START_EVENTS_FORMATTED: # values before START_EVENTS_FORMATTED are corrupted
        relevant_period_start = START_EVENTS_FORMATTED
    
    # select values in relevant event time period -> LABEL = 1
    event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+SQL_PART_ROUTINE+
                                           """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+DEFINITIONNUMBER_ASV+
                                           """ AND StartDateTime >= ? 
                                           AND StartDateTime < ?""", (relevant_period_start, event_time)
                                           ).fetchall()
    for row in event_ASV_unformatted:
        event_ASV.append( [ *( float(i) for i in row[0].split(';')[:NUMBER_ASV_POSITIONS] ) ] )
    
    # preparing for next loop iteration
    prior_event_time = event_time
    display_count += len(event_ASV_unformatted)
    sys.stdout.write("\r#event ASV tupels collected: %i" % display_count)
    sys.stdout.flush()
#####################################


##################################### grab no_event AnalogSignalValues
print('\nstart collecting no_event ASV')
no_event_ASV = []
no_event_period_start = event_time_last + timedelta(hours=TIME_AFTER_LAST_EVENT) 
no_event_period_end = no_event_period_start + timedelta(hours=TIMEFRAME_NO_EVENT_ASV)
# select values in relevant no_event time period -> LABEL = 0
no_event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+SQL_PART_ROUTINE+
                                       """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+DEFINITIONNUMBER_ASV+
                                       """ AND StartDateTime >= ? 
                                       AND StartDateTime < ?""", (no_event_period_start, no_event_period_end)
                                       ).fetchall()
for row in no_event_ASV_unformatted:
        no_event_ASV.append( [ *( float(i) for i in row[0].split(';')[:NUMBER_ASV_POSITIONS] ) ] )
print('#no_event ASV tupels collected:', len(no_event_ASV))
print( 'ranging from %s to %s' % (no_event_period_start.strftime('%Y/%m/%d %H:%M'), no_event_period_end.strftime('%Y/%m/%d %H:%M')) )
print('--%--')
#####################################




##################################### prepare training and test data
from sklearn.model_selection import train_test_split

print('start preparing training and test data')
n_event_ASV = len(event_ASV)
n_no_event_ASV = len(no_event_ASV)
print(n_event_ASV)
data_tuples = np.array(event_ASV)
data_tuples = np.append(data_tuples, no_event_ASV ,axis=0)

labels = np.ones(n_event_ASV)
labels = np.append(labels, np.zeros(n_no_event_ASV), axis=0)

data_train, data_test, labels_train, labels_test = train_test_split(data_tuples,labels,test_size=(1-FRACTION_TRAIN)) # randomize training and test data sets

print('data preparation finished:')
print('training data: %i (event ASV: %i | no_event ASV: %i)' % (len(data_train), sum(labels_train), len(labels_train)-sum(labels_train) ) )
print('test data: %i (event ASV: %i | no_event ASV: %i)' % (len(data_test), sum(labels_test), len(labels_test)-sum(labels_test) ) )
print('--%--')
#####################################



##################################### implement SVM
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn import metrics
# linear
print('start LinearSVC training')
lin_classifier = LinearSVC(dual=False)
lin_classifier.fit(data_train, labels_train)
prediction_lin_classifier = lin_classifier.predict(data_test)
print('LinearSVC training finished')


# rbf
print('start rbf SVC training (duration approx 10 min)')
rbf_classifier = SVC()
rbf_classifier.fit(data_train, labels_train)
prediction_rbf_classifier = rbf_classifier.predict(data_test)
print('rbf SVC training finished')
print('--%--\n')
##################################### 



##################################### evaluation of results
print('evaluation metrics')
# cross validation http://scikit-learn.org/stable/modules/cross_validation.html#computing-cross-validated-metrics
## linear ##
score_lin_classifier = lin_classifier.score(data_test, labels_test) # precision
print('linear classifier\nscore on test data:',score_lin_classifier)

cfm1 = metrics.confusion_matrix(labels_test, prediction_lin_classifier)
#True negative
tn = cfm1[0][0]
#False positive
fp = cfm1[0][1]
#False negative
fn = cfm1[1][0] 
#True positive
tp = cfm1[1][1]
print('confusion matrix:', cfm1, sep='\n')

tpr = tp/(tp+fn)
print('true positive rate:', tpr)
fpr = fp/(fp+tn)
print('false positive rate:', fpr)
classification_error = (fp + fn)/(tp+fp+tn+fn)
print('classification error: ', classification_error)
print('\n')

## rbf ##
score_rbf_classifier = rbf_classifier.score(data_test, labels_test)
print('rbf classifier\nscore on test data:',score_rbf_classifier)

cfm2 = metrics.confusion_matrix(labels_test, prediction_rbf_classifier)
tn = cfm2[0][0]
fp = cfm2[0][1]
fn = cfm2[1][0] 
tp = cfm2[1][1]
print('confusion matrix:', cfm2, sep='\n')

tpr = tp/(tp+fn)
print('true positive rate:', tpr)
fpr = fp/(fp+tn)
print('false positive rate:', fpr)
classification_error = (fp + fn)/(tp+fp+tn+fn)
print('classification error: ', classification_error)
##################################### 







##################################### BACKUP
"""
# quantity of train and test data
n_event_ASV_train = math.ceil(FRACTION_TRAIN*n_event_ASV)
n_event_ASV_test = n_event_ASV - n_event_ASV_train
n_no_event_ASV_train = math.ceil(FRACTION_TRAIN*n_no_event_ASV)
n_no_event_ASV_test = n_no_event_ASV - n_no_event_ASV_train

# train and test labels
labels_train = np.ones(n_event_ASV_train)
temp_zeros = np.zeros(n_no_event_ASV_train)
labels_train = np.append( labels_train, temp_zeros, axis = 0 )
labels_test = np.ones(n_event_ASV_test)
temp_zeros = np.zeros(n_no_event_ASV_test)
labels_test = np.append( labels_test, temp_zeros, axis = 0 )

# train and test data tupels
data_train = np.array(event_ASV[:n_event_ASV_train])
data_train = np.append( data_train, no_event_ASV[:n_no_event_ASV_train], axis=0 )
#print(data_train)
#print('%i soll sein %i soll sein %i' % (len(data_train), n_event_ASV_train+n_no_event_ASV_train, len(labels_train)) )
#print('\n\n\n')
data_test = np.array(event_ASV[n_event_ASV_train:])
data_test = np.append( data_test, no_event_ASV[n_no_event_ASV_train:], axis=0 )
#print(data_test)
#print('%i soll sein %i soll sein %i' % (len(data_test), n_event_ASV_test+n_no_event_ASV_test, len(labels_test)) )
#print('\n\n\n')
"""