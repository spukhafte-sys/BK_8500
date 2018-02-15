

import csv
import os
import time

class data_logging:

    def __init__(self, header_list, log_file_postfix=''):

        self.log_file = 'data_log_' + log_file_postfix + '.csv'
        self.log_file_header = header_list

        if os.path.exists(self.log_file) is not True:
            with open(self.log_file, mode='a') as the_file:
                writer = csv.writer(the_file, dialect='excel')
                writer.writerow(header_list)

    def write_data(self, data_list, debug=True):

        if debug is True:
            print(data_list)

        with open(self.log_file, mode='a') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(data_list)
