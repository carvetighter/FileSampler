#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#
# File / Package Import
#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$# 

import csv
import random
from numpy import mean
from io import StringIO

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#
# Classes
#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#

"""
This script contains two classes RandomAccessReader and CsvRandomAccessReader.

The goal of these classes is to ramdom sample a file with little overhead.  
RandomAccessReader is the base class for the CsvRandomAccessReader.  
"""

class RandomAccessReader(object):

    def __init__(self, filepath, endline_character = '\n', ignore_blank_lines = False):
        """
        :param filepath:  Absolute path to file
        :param endline_character: Delimiter for lines. Defaults to newline character (\n)
        """
        self._filepath = filepath
        self._endline = endline_character
        self._ignore_blanks = ignore_blank_lines
        self._int_num_lines = 123000000
        #self._int_num_lines = self._count_lines()
        self._int_avg_len = self._get_avg_len()

    @property
    def number_of_lines(self):
        return _int_num_lines

    def get_line_indexes(self):
        return range(len(self._lines))

    def _count_lines(self):
        return sum(1 for line in open(self._filepath))

    def _get_avg_len(self):
        f = open(self._filepath)
        # for the header row
        f.readline()

        # read first 10 lines
        list_lines = []
        if self._int_num_lines < 11:
            list_lines.append(len(f.readline()))
        else:
            for int_line_num in range(0, 10):
                    list_lines.append(len(f.readline()))
        
        # calc temp mean
        int_temp_mean = int(mean(list_lines)) + 1
        
        # get 100 random lines to test
        list_random_lines = list()
        for int_dummy in range(0, 100):
            list_random_lines.append(random.randint(0, self._int_num_lines - 1))

        # read 100 lines for sampling of average line length
        list_len_100_lines = list()
        for int_line_num in list_random_lines:
            # check for last line last line
            if int_line_num == self._int_num_lines - 1:
                int_line_num -= 1

            # go to character in file
            f.seek(int(int_line_num * int_temp_mean))
            
            # read partial line then read entire line
            f.readline()
            list_len_100_lines.append(len(f.readline()))
        f.close()

        return int(mean(list_len_100_lines))

    def get_lines(self, line_number, amount = 1):
        """
        get the contents of a given line in the file
        :param line_number: 0-indexed line number
        :param amount amount of lines to read
        :return: str
        """
        lines = []
        with open(self._filepath) as f:
            for x in range(0, amount):
                f.seek(line_number * self._int_avg_len)
                f.readline()
                lines.append(f.readline())
            return lines

class CsvRandomAccessReader(RandomAccessReader):

    def __init__(self, filepath, has_header = True, **kwargs):
        """
        :param filepath:
        :param has_header:
        :param kwargs: endline_character='\n', values_delimiter=',', 
        quotechar='"', ignore_corrupt=False, ignore_blank_lines=True
        """
        super(CsvRandomAccessReader, self).__init__(filepath, kwargs.get('endline_character','\n'), 
                                                    kwargs.get('ignore_blank_lines', True))
        self._headers = None
        self._delimiter = kwargs.get('values_delimiter', ',')
        self._quotechar = kwargs.get('quotechar', '"')
        self._ignore_bad_lines = kwargs.get('ignore_corrupt', False)
        self.has_header = has_header
        if has_header:
            dialect = self.MyDialect(self._endline, self._quotechar, self._delimiter)
            b = StringIO(self.get_lines(0)[0])
            r = csv.reader(b, dialect)
            values = tuple(next(r))
            self._headers = values

    @property
    def headers(self):
        return self._headers

    def set_headers(self, header_list):
        if not hasattr(header_list, '__iter__'):
            raise TypeError("Argument 'header_list' must contain an iterable")
        self._headers = tuple(header_list)

    def _get_line_values(self, line):
        """
        Splits the csv line into a list of individual values
        :param line: str
        :return: tuple of str
        """
        dialect = self.MyDialect(self._endline, self._quotechar, self._delimiter)
        b = StringIO(line)
        r = csv.reader(b, dialect)
        values = tuple(next(r))
        if len(self._headers) != len(values):
            if not self._ignore_bad_lines:
                raise ValueError("Corrupt csv - header and row have different lengths")
            return None
        return values

    def get_line_dicts(self, line_number, amount=1):
        """
        gets the requested line as a dictionary (header values are the keys)
        :param line_number: requested line number, 0-indexed (disregards the header line if present)
        :param amount
        :return: dict
        """
        if not self._headers:
            raise ValueError("Headers must be set before requesting a line dictionary")
        if self.has_header:
            line_number += 1
        lines = []
        text_lines = self.get_lines(line_number, amount)
        for x in range(0, amount):
            vals = self._get_line_values(text_lines[x])
            if vals is None:
                lines.append(dict(zip(self._headers, list(range(len(self._headers))))))
            else:
                lines.append(dict(zip(self._headers, vals)))
        return lines

    class MyDialect(csv.Dialect):
        strict = True
        skipinitialspace = True
        quoting = csv.QUOTE_ALL
        delimiter = ','
        quotechar = '"'
        lineterminator = '\n'

        def __init__(self, terminator, quotechar, delimiter):
            csv.Dialect.__init__(self)
            self.delimiter = delimiter
            self.lineterminator = terminator
            self.quotechar = quotechar
