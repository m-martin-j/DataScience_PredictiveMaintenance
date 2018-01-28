from datetime import datetime, timedelta

# operations processing database analog signal values and digital signal values


DEFAULT_START_TIME = datetime.strptime( '1900-01-01', "%Y-%m-%d") # to not set constraints for first event time stamp



def get_event_time_stamps(cursor, sql_part_routine, definition_nbr_event, start_events=DEFAULT_START_TIME):
    # grab and format event time stamps
    event_times_unformatted = cursor.execute("""SELECT StartDateTime """+sql_part_routine+
                                            """ AND TriggerSignalValue = 1  -- otherwise each alarm time is selected twice
                                            AND DiagnosticDataSetDefinition.DefinitionNumber = """+definition_nbr_event+"""
                                            AND StartDateTime >= ?   
                                            ORDER BY StartDateTime ASC""", (start_events)
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

    return event_times, event_time_first, event_time_last