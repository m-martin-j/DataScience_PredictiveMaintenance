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
DEFINITIONNUMBER_EVENT_1 = 111 # consult SQL-query "get_DefinitionNumber_and_respective_DinGroup" to find the correct DefinitionNumber
DEFINITIONNUMBER_EVENT_2 = 21
DEFINITIONNUMBER_ASV = '2'
NUMBER_ASV_POSITIONS = 2 # only the first NUMBER_ASV_POSITIONS positions of ASV string are relevant

TIMEFRAME_EVENT_ASV = 3*24 # hours

TIMEFRAME_NO_EVENT_ASV = 16*24 # hours 
TIME_BEFORE_FIRST_EVENT = 5*24 + TIMEFRAME_NO_EVENT_ASV # hours (no_event values start at that point of time)
MIN_INTERMEDIATE_TIMEFRAME_NO_EVENT_ASV = 2*24 # hours
MIN_DELTA_TWO_EVENTS = 2* 7.22*24 + MIN_INTERMEDIATE_TIMEFRAME_NO_EVENT_ASV # minimum time (in hours) between two events to grab no_event values between them

FRACTION_TRAIN = 0.1 # fraction of examples that will be train data
FRACTION_TEST = 0.2

NORMALIZE = False # to normalize or not to normalize ASV
K = 5 # Parameter k for k-fold cross validation

MAX_ASV1 = 5000 # to carefully üpurge undefined values
MAX_ASV2 = 5000


# following SQL queries execute relevant joins w/o SELECT statement
SQL_PART_ROUTINE =  """FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
                  WHERE ReadOut.FK_Vehicle = """+VEHICLE_NUMBER
#####################################

print('-----------------------\nSVM on Concerto Data\napproach: ENGINE 1\n-----------------------')



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
                                        AND DiagnosticDataSetDefinition.DefinitionNumber in (?,?)
                                        ORDER BY StartDateTime ASC""", (DEFINITIONNUMBER_EVENT_1, DEFINITIONNUMBER_EVENT_2) 
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
print('Number of events: %s,\nranging from %s to %s (delta: %s)' % (n_event_times, event_times[0].strftime('%Y/%m/%d %H:%M'), event_times[-1].strftime('%Y/%m/%d %H:%M'), event_time_diff) )
print('--%--')
#####################################



##################################### grab event AnalogSignalValues and intermediate no_event time periods
print('start collecting event ASV')
prior_event_time = 0
event_ASV = [] # array containing event ASV tupels
interm_periods_no_event = [] # array containing 
display_count = 0 # counter for command line output

for event_time in event_times:
    # calculate relevant time period before event for event values
    relevant_period_start = event_time - timedelta(hours=TIMEFRAME_EVENT_ASV)
    if prior_event_time != 0 and prior_event_time >= relevant_period_start: # less than TIMEFRAME_EVENT_ASV hours between two events
        relevant_period_start = prior_event_time
    
    # select event values in relevant event time period -> LABEL = 1
    event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+SQL_PART_ROUTINE+
                                           """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+DEFINITIONNUMBER_ASV+
                                           """ AND StartDateTime >= ? 
                                           AND StartDateTime < ?""", (relevant_period_start, event_time)
                                           ).fetchall()
    for row in event_ASV_unformatted:
        event_ASV.append( [ *( float(i) for i in row[0].split(';')[:NUMBER_ASV_POSITIONS] ) ] )
        if event_ASV[-1][0] >= MAX_ASV1 or event_ASV[-1][1] >= MAX_ASV2: # delete undefined values
            del event_ASV[-1]
    

    # calculate time period between two events for intermediate no_event values
    if prior_event_time != 0:
        delta_two_events = event_time - prior_event_time
        if delta_two_events >= timedelta(hours=MIN_DELTA_TWO_EVENTS):
            interm_relevant_period_no_event_start = prior_event_time + timedelta(hours=(MIN_DELTA_TWO_EVENTS-MIN_INTERMEDIATE_TIMEFRAME_NO_EVENT_ASV)/2.0)
            interm_relevant_period_no_event_end = event_time - timedelta(hours=(MIN_DELTA_TWO_EVENTS-MIN_INTERMEDIATE_TIMEFRAME_NO_EVENT_ASV)/2.0)
            interm_periods_no_event.append([interm_relevant_period_no_event_start, interm_relevant_period_no_event_end])

    # preparing for next loop iteration
    prior_event_time = event_time
    display_count += len(event_ASV_unformatted)
    sys.stdout.write("\r#event ASV tupels collected: %i" % display_count)
    sys.stdout.flush()
#####################################



##################################### grab no_event AnalogSignalValues
print('\nstart collecting no_event ASV')
no_event_ASV = []
no_event_period_start = event_time_first - timedelta(hours=TIME_BEFORE_FIRST_EVENT) 
no_event_period_end = no_event_period_start + timedelta(hours=TIMEFRAME_NO_EVENT_ASV)

# select values in relevant no_event time period BEFORE events -> LABEL = 0
no_event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+SQL_PART_ROUTINE+
                                       """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+DEFINITIONNUMBER_ASV+
                                       """ AND StartDateTime >= ? 
                                       AND StartDateTime < ?""", (no_event_period_start, no_event_period_end)
                                       ).fetchall()
for row in no_event_ASV_unformatted:
    no_event_ASV.append( [ *( float(i) for i in row[0].split(';')[:NUMBER_ASV_POSITIONS] ) ] )
    if no_event_ASV[-1][0] >= MAX_ASV1 or no_event_ASV[-1][1] >= MAX_ASV2: # delete undefined values
            del no_event_ASV[-1]

# select values in relevant no_event time period BETWEEN events -> LABEL = 0
display_count = len(no_event_ASV)
for interm_no_event in interm_periods_no_event:
    no_event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+SQL_PART_ROUTINE+
                                       """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+DEFINITIONNUMBER_ASV+
                                       """ AND StartDateTime >= ? 
                                       AND StartDateTime < ?""", (interm_no_event[0],interm_no_event[1])
                                       ).fetchall()    
    for row in no_event_ASV_unformatted:
        no_event_ASV.append( [ *( float(i) for i in row[0].split(';')[:NUMBER_ASV_POSITIONS] ) ] )
        if no_event_ASV[-1][0] >= MAX_ASV1 or no_event_ASV[-1][1] >= MAX_ASV2: # delete undefined values
            del no_event_ASV[-1]
    display_count += len(no_event_ASV_unformatted)
    sys.stdout.write("\r#no_event ASV tupels collected: %i" % display_count)
    sys.stdout.flush()

#print( '\nranging from %s to %s' % (no_event_period_start.strftime('%Y/%m/%d %H:%M'), no_event_period_end.strftime('%Y/%m/%d %H:%M')) )
#####################################
print('\n--%--')



##################################### prepare training and test data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize

print('start preparing training and test data')
n_event_ASV = len(event_ASV)
n_no_event_ASV = len(no_event_ASV)
data_tuples = np.array(event_ASV)
data_tuples = np.append(data_tuples, no_event_ASV ,axis=0)

labels = np.ones(n_event_ASV)
labels = np.append(labels, np.zeros(n_no_event_ASV), axis=0)

data_train, data_test, labels_train, labels_test = train_test_split(data_tuples,labels,train_size=FRACTION_TRAIN, test_size=FRACTION_TEST) # randomize training and test data sets

if NORMALIZE: # normalize
    data_train = normalize(data_train, copy=False)
    data_test = normalize(data_test, copy=False)
    print('normalized ', end='')

print('data preparation finished:')
print('training data: %i (event ASV: %i | no_event ASV: %i)' % (len(data_train), sum(labels_train), len(labels_train)-sum(labels_train) ) )
print('test data: %i (event ASV: %i | no_event ASV: %i)' % (len(data_test), sum(labels_test), len(labels_test)-sum(labels_test) ) )
print('--%--')
#####################################



##################################### implement SVM
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn import metrics
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.model_selection import cross_val_score

# linear
print('start Linear SVC training')
lin_classifier = LinearSVC(dual=False, C=1)
lin_classifier.fit(data_train, labels_train)
prediction_lin_classifier = lin_classifier.predict(data_test)
print('--Linear SVC training finished')


# rbf
print('start rbf SVC training (duration approx. 1h)')
rbf_classifier = SVC(cache_size=1000) # increase memory available for this classifier (default: 200MB)
rbf_classifier.fit(data_train, labels_train)
prediction_rbf_classifier = rbf_classifier.predict(data_test)
print('--rbf SVC training finished')
n_sv = rbf_classifier.n_support_
print('Nbr. of support vectors of respective classes (available only for nonlinear SVC):\nevent values: %i vectors; no_event values: %i vectors' %(n_sv[1], n_sv[0]))
print('--%--\n')
##################################### '''



##################################### evaluation of results
print('evaluation metrics:\n')
## linear ##
score_lin_classifier = lin_classifier.score(data_test, labels_test) # precision
print('LINEAR CLASSIFIER\nscore on test data:',score_lin_classifier)

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

# Error on Training data
prediction_lin_classifier_train = lin_classifier.predict(data_train)
classification_error_train_lin = 1.0 - metrics.accuracy_score(labels_train, prediction_lin_classifier_train, normalize=True)
print('(classification error on training data: %0.12f)' % classification_error_train_lin)

# cross validation
print('started %s-fold cross validation' % K)
scores = cross_val_score(lin_classifier, data_tuples, labels, cv=K)
print('cross validation finished: score: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std() * 2))

'''# ROC curve lin_classifier
print('ROC curve will be shown in a separate window - in order to proceed with the evaluation report, please CLOSE the ROC curve window!\n')
y_score = lin_classifier.decision_function(data_train)
fpr, tpr, threshold = metrics.roc_curve(labels_train, y_score)
roc_auc = metrics.auc(fpr, tpr)
plt.title('Receiver Operating Characteristic Linear Classifier')
plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()'''



'''# create scatter plot Train
x_min, x_max = data_train[:, 0].min() - .5, data_train[:, 0].max() + 5
y_min, y_max = data_train[:, 1].min() - .5, data_train[:, 1].max() + 5
plt.figure(figsize=(8, 6))
plt.clf()
plt.scatter(data_train[:, 0], data_train[:, 1], c=labels_train, edgecolor='k')
plt.xlabel('revolutions per minute')
plt.ylabel('coolant temperature [°C]')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.show()
# create scatter plot total
x_min, x_max = data_tuples[:, 0].min() - .5, data_tuples[:, 0].max() + 5
y_min, y_max = data_tuples[:, 1].min() - .5, data_tuples[:, 1].max() + 5
plt.figure(figsize=(8, 6))
plt.clf()
plt.scatter(data_tuples[:, 0], data_tuples[:, 1], c=labels, s=(mpl.rcParams['lines.markersize'] ** 2)/8, edgecolor='k')
plt.xlabel('revolutions per minute')
plt.ylabel('coolant temperature [°C]')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.show()
# create scatter plot total normalized
data_tuples = normalize(data_tuples, copy=False)
x_min, x_max = data_tuples[:, 0].min() - .5, data_tuples[:, 0].max() + .5
y_min, y_max = data_tuples[:, 1].min() - .5, data_tuples[:, 1].max() + .5
plt.figure(figsize=(8, 6))
plt.clf()
plt.scatter(data_tuples[:, 0], data_tuples[:, 1], c=labels, s=(mpl.rcParams['lines.markersize'] ** 2)/8, edgecolor='k')
plt.xlabel('revolutions per minute')
plt.ylabel('coolant temperature [°C]')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.show()'''


## rbf ##
score_rbf_classifier = rbf_classifier.score(data_test, labels_test)
print('RBF CLASSIFIER\nscore on test data:',score_rbf_classifier)

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

# Error on Training data
prediction_rbf_classifier_train = rbf_classifier.predict(data_train)
classification_error_train_rbf = 1.0 - metrics.accuracy_score(labels_train, prediction_rbf_classifier_train, normalize=True)
print('(classification error on training data: %0.12f)' % classification_error_train_rbf)

# ROC curve rbf_classifier
print('ROC curve will be shown in a separate window - in order to proceed with the evaluation report, please CLOSE the ROC curve window!\n')
y_score = rbf_classifier.decision_function(data_train)
fpr, tpr, threshold = metrics.roc_curve(labels_train, y_score)
roc_auc = metrics.auc(fpr, tpr)
plt.title('Receiver Operating Characteristic RBF Classifier')
plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()
#####################################'''




## BACKUP ##
"""START_EVENTS_FORMATTED = datetime.strptime( '2017-01-17', "%Y-%m-%d") # point of time of very first event AND event ASV
if relevant_period_start < START_EVENTS_FORMATTED: # values before START_EVENTS_FORMATTED are corrupted  TODO
        relevant_period_start = START_EVENTS_FORMATTED


# cross validation
print('started %s-fold cross validation (duration > 5h)' % K)
scores = cross_val_score(rbf_classifier, data_tuples, labels, cv=K)
print('cross validation finished: score: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std() * 2))

"""
