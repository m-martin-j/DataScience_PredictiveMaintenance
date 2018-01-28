import sys
import os
import errno
from datetime import datetime

# store and load lists, arrays


def make_data_dir():
    directory = '__cached_data__/'
    if not os.path.exists(os.path.dirname(directory)):
        try:
            os.makedirs(os.path.dirname(directory))
            return True
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
            print('ERROR: could not create cached_data folder')
            input("Press Enter to continue...")
            sys.exit(0)
    else: # directory exists
        return True


def store_list(list,filename):
    try: 
        f = open('__cached_data__/'+filename+'.tmp','w')
    except IOError:
        print('ERROR: could not create file')
        return
    for line in list:
        f.write(str(line))
        f.write('\n')
    f.close()


def load_list(filename, readtype = 'numeric', columns = 1):
    try:
        f = open('__cached_data__/'+filename+'.tmp','r')
    except:
        print('ERROR: could not read file')
    list = []
    for line in f:
        tmp = line.strip()
        if readtype == 'time':
            element = datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S.%f")
        if readtype == 'numeric':
            #element = ...columns...
            pass
        list.append(element)

    if readtype == 'time':
        first = list[0]
        last = list[-1]
        return list, first, last
    else:
        return list

