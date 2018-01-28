import sys
import os
import errno
from datetime import datetime

# store and load lists, arrays


DEFAULT_DIR_NAME = '__cached_data__/'


def make_data_dir(directory = DEFAULT_DIR_NAME):    
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


def check_dir(directory = DEFAULT_DIR_NAME):
    if os.path.exists(os.path.dirname(directory)):
        return True
    else:
        return False


def store_list(list,filename, writetype = 'numeric'):
    try: 
        f = open('__cached_data__/'+filename+'.tmp','w')
    except IOError:
        print('ERROR: could not create file')
        input("Press Enter to continue...")
        sys.exit(0)
    for line in list:
        if writetype == 'time':
            f.write(str(line))
        if writetype == 'numeric':
            for i, value in enumerate(line):
                if not i==len(line)-1:
                    f.write(str(value))
                    f.write(';')
                else:
                    f.write(str(value))
        f.write('\n')
    f.close()


def load_list(filename, readtype = 'numeric'):
    try:
        f = open('__cached_data__/'+filename+'.tmp','r')
    except:
        print('ERROR: could not read file')
        input("Press Enter to continue...")
        sys.exit(0)
    list = []
    for line in f:
        tmp = line.strip()
        if readtype == 'time':
            element = datetime.strptime(tmp, "%Y-%m-%d %H:%M:%S.%f")
        if readtype == 'numeric':
            element = [ *( float(i) for i in tmp.split(';') ) ]
        list.append(element)
    f.close()
    if readtype == 'time':
        first = list[0]
        last = list[-1]
        return list, first, last
    else:
        return list