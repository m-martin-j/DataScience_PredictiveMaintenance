from datetime import datetime, timedelta
import sys
import numpy as np
from sklearn.model_selection import train_test_split

# operations processing database analog signal values and digital signal values


DEFAULT_START_TIME = datetime.strptime( '1900-01-01', "%Y-%m-%d") # to not set constraints for first event time stamp



def get_event_time_stamps(cursor, sql_part_routine, definition_nbr_event, start_events = DEFAULT_START_TIME):
    # grab and format event time stamps
    event_times_unformatted = cursor.execute("""SELECT StartDateTime """+sql_part_routine+
                                            """ AND TriggerSignalValue = 1  -- otherwise each alarm time is selected twice
                                            AND DiagnosticDataSetDefinition.DefinitionNumber = """+definition_nbr_event+"""
                                            AND StartDateTime >= ?   
                                            ORDER BY StartDateTime ASC""", (start_events)
                                            ).fetchall()
    print('Event time stamps collected')
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

    return event_times, event_time_first, event_time_last


def get_event_ASV(cursor, event_times, timeframe_event_ASV, number_ASV_positions, sql_part_routine, definitionnumber_ASV, earliest_valid_ASV = DEFAULT_START_TIME):
    print('start collecting event ASV')
    prior_event_time = 0
    event_ASV = [] # array containing event ASV tupels
    display_count = 0 # counter for command line output

    for event_time in event_times:
        # calculate relevant time period before event
        relevant_period_start = event_time - timedelta(hours=timeframe_event_ASV)
        if prior_event_time != 0 and prior_event_time >= relevant_period_start: # less than timeframe_event_ASV hours between two events
            relevant_period_start = prior_event_time

        if relevant_period_start < earliest_valid_ASV: # values before timestamp earliest_valid_ASV are ignored
            relevant_period_start = earliest_valid_ASV
    
        # select values in relevant event time period -> LABEL = 1
        event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+sql_part_routine+
                                               """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+definitionnumber_ASV+
                                               """ AND StartDateTime >= ? 
                                               AND StartDateTime < ?""", (relevant_period_start, event_time)
                                               ).fetchall()
        for row in event_ASV_unformatted:
            event_ASV.append( [ *( float(i) for i in row[0].split(';')[:number_ASV_positions] ) ] )
    
        # preparing for next loop iteration
        prior_event_time = event_time
        display_count += len(event_ASV_unformatted)
        sys.stdout.write("\r#event ASV tupels collected: %i" % display_count)
        sys.stdout.flush()

    print('\n')
    return event_ASV


def get_no_event_ASV(cursor, event_time, relaxation_time, timeframe_no_event_ASV, sql_part_routine, definitionnumber_ASV, number_ASV_positions, approach = 'before'):
    print('start collecting no_event ASV')
    no_event_ASV = []
    if approach == 'before': # default: collect no_event ASV in time period before alarms occured
        pass
    if approach == 'after': # collect no_event ASV in time period after alarms occured
        no_event_period_start = event_time + timedelta(hours=relaxation_time) 
    no_event_period_end = no_event_period_start + timedelta(hours=timeframe_no_event_ASV)
    # select values in relevant no_event time period -> LABEL = 0
    no_event_ASV_unformatted = cursor.execute("""SELECT EnvironmentDataSet.AnalogSignalValues """+sql_part_routine+
                                           """ AND DiagnosticDataSetDefinition.DefinitionNumber = """+definitionnumber_ASV+
                                           """ AND StartDateTime >= ? 
                                           AND StartDateTime < ?""", (no_event_period_start, no_event_period_end)
                                           ).fetchall()
    for row in no_event_ASV_unformatted:
            no_event_ASV.append( [ *( float(i) for i in row[0].split(';')[:number_ASV_positions] ) ] )
    print('#no_event ASV tupels collected:', len(no_event_ASV))
    print( 'ranging from %s to %s' % (no_event_period_start.strftime('%Y/%m/%d %H:%M'), no_event_period_end.strftime('%Y/%m/%d %H:%M')) )

    return no_event_ASV


def create_train_test_data(event_ASV, no_event_ASV, fraction_test, fraction_train=0):
    # create numpy data and label array
    print('start data preparation')
    n_event_ASV = len(event_ASV)
    n_no_event_ASV = len(no_event_ASV)
    data_tuples = np.array(event_ASV)
    data_tuples = np.append(data_tuples, no_event_ASV ,axis=0)

    labels = np.ones(n_event_ASV)
    labels = np.append(labels, np.zeros(n_no_event_ASV), axis=0)
    print('data and label array created')
    
    if fraction_train == 0:
        data_train, data_test, labels_train, labels_test = train_test_split(data_tuples,labels,test_size=fraction_test) # randomize training and test data sets
    else:
        data_train, data_test, labels_train, labels_test = train_test_split(data_tuples,labels,train_size=fraction_train, test_size=fraction_test)

    print('data preparation finished:')
    print('training data: %i (event ASV: %i | no_event ASV: %i)' % (len(data_train), sum(labels_train), len(labels_train)-sum(labels_train) ) )
    print('test data: %i (event ASV: %i | no_event ASV: %i)' % (len(data_test), sum(labels_test), len(labels_test)-sum(labels_test) ) )
    print('--%--')
    
    return data_train, data_test, labels_train, labels_test