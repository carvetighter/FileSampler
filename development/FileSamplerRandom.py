#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#
# File / Package Import
#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$# 

import csv
from random import randrange
from pandas import DataFrame, Series
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

class FileSamplerBase(object):

    def __init__(self, m_string_filepath, m_string_endline_character = '\n', m_bool_estimate = False):
        """
        this method initialized the base class for the text file sampler; class will attempt to map the file
        for the start character of the line and the length of each line; if the file is more than 1 million lines 
        this method will estimate the length of the line through sampling 1000 rows
        
        Requirements:
        package numpy.mean
        
        Inputs:
        m_string_filepath
        Type: string
        Desc: absolute file path, includes file name

        m_string_endline_character
        Type: string
        Desc: end of line character for the file

        m_bool_estimate
        Type: boolean
        Desc: flag to indicate if the mode of line retrievela is by estimating the line length or 
            use list of dictionaries for line start position and line length
        
        Important Info:
        None
        
        Objects and Properties:
        _string_filepath
        Type: string
        Desc: absolute file path

        _string_endline
        Type: string
        Desc: end of line character

        _int_num_lines
        Type: integer
        Desc: number of lines in the file

        _int_avg_len
        Type: integer
        Desc: average length of the file; only used in estimation of line lenght mode

        _bool_estimate_mode
        Type: boolean
        Desc: flag to indicate if the mode of line retrievela is by estimating the line length or 
            use list of dictionaries for line start position and line length

        _list_line_indexes
        Type: list of dictionaries
        Desc: each dictionary contines the character number for the start of the line and the length of the line; 
            the index of the list is the line number starting at 0; this is only if the number of lines in the file
            is less than 1 million
        _list_line_indexes[x] -> {'start': <integer>, 'length':<integer>}
        
        eg: _list_line_indexes[3] -> {'start':57, 'length':23}
        """
        self._string_filepath = m_string_filepath
        self._string_endline = m_string_endline_character
        self._bool_estimate_mode = m_bool_estimate

        if self._bool_estimate_mode:
            self._int_num_lines = self._count_lines()
            self._int_avg_len = self._get_avg_len()
            self._list_line_indexes = None
        else:
            try:
                self._list_line_indexes = self._build_line_indexes()
            except AttributeError as ae:
                self._int_num_lines = self._count_lines()
                self._int_avg_len = self._get_avg_len()
                self._list_line_indexes = None
                self._bool_estimate_mode = True
            else:
                self._int_num_lines = len(self._list_line_indexes)
                self._int_avg_len = None
            finally:
                pass

    @property
    def number_of_lines(self):
        return self._int_num_lines

    @property
    def estimate_mode(self):
        return self._bool_estimate_mode

    def get_line_indexes(self):
        return range(0, len(self._list_line_indexes))

    def _count_lines(self):
        return sum(1 for line in open(self._filepath))

    def _get_avg_len(self):
        """
        this method calculates the an average line length by sampling 1000 random lines from the file
    
        Requirements:
        package numpy.mean
    
        Inputs:
        None
        Type: n/a
        Desc: n/a
        
        Important Info:
        None
    
        Return:
        variable
        Type: integer
        Desc: average length of the sample of lines
        """
        with open(self._string_filepath, 'r') as file:
            # read first 10 lines
            list_lines = []
            for int_line_num in range(0, 10):
                    list_lines.append(len(file.readline()))
        
            # calc temp mean
            int_temp_mean = int(mean(list_lines))
        
            # get 1000 random lines to test
            list_random_lines = [randrange(0, self._int_num_lines) for x in range(0, 1000)]

            # read 1000 lines for sampling of average line length
            list_len_1000_lines = list()
            for int_line_num in list_random_lines:
                # go to line before random line
                if int_line_num == 0:
                    int_line_start = 0
                else:
                    int_line_start = int_line_num * int_temp_mean - int(0.5 * int_temp_mean)
                f.seek(int_line_start)
            
                # read partial line then read entire line
                if int_line_start != 0:
                    file.readline()
                list_len_1000_lines.append(len(file.readline()))

        return int(mean(list_len_1000_lines))

    def _build_line_indexes(self):
        """
        this method calculates the character index, integer, of the start of the line and the line length of each line
        in the file; if the file is more than 1 million rows the method will only count the number of rows and switch
        to an estimation mode
    
        Requirements:
        None
    
        Inputs:
        None
        
        Important Info:
        None
    
        Return:
        object
        Type: list of dictionaries
        Desc: each dictionary contines the character number for the start of the line and the length of the line; 
            the index of the list is the line number starting at 0; this is only if the number of lines in the file
            is less than 1 million
        _list_line_indexes[x] -> {'start': <integer>, 'length':<integer>}
        
        eg: _list_line_indexes[3] -> {'start':57, 'length':23}
        """
        list_lines = list()
        int_line_count = 1
        int_start_posit = 0

        with open(self._string_filepath, 'r') as file:
            for string_line in file:
                int_line_length = len(string_line)
                list_lines.append({'start':int_start_posit, 'length':int_line_length})
                int_start_posit += int_line_length

                # check line count
                if int_line_count > 1000000:
                    raise AttributeError('surpassed line count threashold; 1000000')
                int_line_count += 1

        return list_lines

    def _get_line(self, m_int_line_number, m_file):
        """
        get the contents of a given line in the file
        :param line_number: 0-indexed line number
        :return: str
        """
        if m_int_line_number == 0:
            m_file.seek(m_int_line_number)
        else:
            m_file.seek(m_int_line_number * self._int_avg_len - int(self._int_avg_len / 2))
            m_file.readline()
        return m_file.readline()

class CsvRandomAccessReader(RandomAccessReader):

    def __init__(self, filepath, has_header = True, **kwargs):
        """
        :param filepath:
        :param has_header:
        :param kwargs: endline_character = '\n', values_delimiter = ',', 
        quotechar = '"', ignore_corrupt = False, ignore_blank_lines = True
        """
        super(CsvRandomAccessReader, self).__init__(filepath, kwargs.get('endline_character','\n'), 
                                                    kwargs.get('ignore_blank_lines', True))
        self._headers = None
        self._delimiter = kwargs.get('values_delimiter', ',')
        self._quotechar = kwargs.get('quotechar', '"')
        self._ignore_bad_lines = kwargs.get('ignore_corrupt', False)
        self.has_header = has_header
        if has_header:
            with open(self._filepath) as f:
                self._headers = self._csv_trans(self._get_line(0, f))

    @property
    def headers(self):
        return self._headers

    def set_headers(self, header_list):
        if not hasattr(header_list, '__iter__'):
            raise TypeError("Argument 'header_list' must contain an iterable")
        self._headers = tuple(header_list)

    def _csv_trans(self, string_line):
        dialect = self.MyDialect(self._endline, self._quotechar, self._delimiter)
        b = StringIO(string_line)
        r = csv.reader(b, dialect)
        return tuple(next(r))

    def _get_line_values(self, line):
        """
        Splits the csv line into a list of individual values
        :param line: str
        :return: tuple of str
        """
        values = self._csv_trans(line)
        if len(self._headers) != len(values):
            if not self._ignore_bad_lines:
                raise ValueError("Corrupt csv - header and row have different lengths")
            return None
        return values

    def get_csv_sample(self, m_int_num_samples):
        """
        gets the requested line as a dictionary (header values are the keys)
        :param m_int_num_samples: requested line number, 0-indexed (disregards the header line if present)
        :return: list of tuples
        """
        if m_int_num_samples > self._int_num_lines:
            raise ValueError('Number of samples requested is more than the number of lines in the file')

        if self.has_header:
            list_random_lines = random.sample(range(1, self._int_num_lines), m_int_num_samples)
        else:
            list_random_lines = random.sample(range(0, self._int_num_lines), m_int_num_samples)
        
        list_lines = []
        with open(self._filepath) as f:
            for int_line in list_random_lines:
                text_line = self._get_line(int_line, f)
                list_lines.append(self._get_line_values(text_line))

        #vals = self._get_line_values(text_lines[x])
        #if vals is None:
        #    lines.append(dict(zip(self._headers, list(range(len(self._headers))))))
        #else:
        #    lines.append(dict(zip(self._headers, vals)))
        return list_lines

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
