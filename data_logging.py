

import csv
import os


class data_logging:

    def __init__(self, header_list, log_file="data_log.csv"):

        self.log_file = log_file
        self.log_file_header = header_list

        if os.path.exists(self.log_file) is not True:
            with open(self.log_file, mode='a') as the_file:
                writer = csv.writer(the_file, dialect='excel')
                writer.writerow(header_list)

    def write_data(self, data_list):

        with open(self.log_file, mode='a') as the_file:
            writer = csv.writer(the_file, dialect='excel')
            writer.writerow(data_list)
