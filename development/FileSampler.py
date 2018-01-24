"""
This is the pythone class file for FileSamplerBase, TextSampler and CSVSampler.  These classes make up
the classes needed to sample files at random.  This will help if there is not enough memory to fit into a
DataFrame or Numpy array.  The goal of this project is to be able to efficeintly and effectively sample very
large files.

If the file is over 1 million lines the class will estimate the line length for data / line reteival.  If the file is less 
than 1 million lines a dictionary is used to track the line length and first position of the line in the file.  At about 
a million lines the dictionary takes up about ~80 MB of space. 

GitHub Repo: https://github.com/carvetighter/FileSampler

Basic Usage:
from FileSampler import TextSampler
from FileSampler import CsvSampler
import pandas

# Text file sampling
txt_reader = RandomAccessReader(string_file) # must include path if not in home directory

string_single_line = txt_reader.get_a_line(33) # retrieves the 33rd line of the file
list_multiple_lines = txt_reader.get_lines([5, 15, 33, 789]) # retrieves the 4 lines from the file
list_random_lines = txt_reader.get_random_lines(15) # retrieves 15 random lines; this is sample with replacement

# Csv file sampling
csv_reader = CsvRandomAccessReader(string_file) # must include path if not in home directory

"""

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
        if self._bool_estimate_mode:
            return None
        else:
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

class TextSampler(FileSamplerBase):

    def __init__(self, m_string_filepath, bool_has_header, **kwargs):
        """
        """
        super(FileSamplerBase, self).__init__(m_string_filepath,
                                                                      kwargs.get('m_string_endline_character', '\n'),
                                                                      kwargs.get('m_bool_estimate', False))

    def get_a_line(self, m_int_line_number):
        '''
        this method will recreive a line from the text file
    
        Requirements:
        class FileSamplerBase
    
        Inputs:
        m_int_line_number
        Type: int
        Desc: line number of the file
        
        Important Info:
        None
    
        Return:
        variable
        Type: string
        Desc: line desired from the text file
        '''
        with open(self._string_filepath, 'r') as file:
            if self._bool_estimate_mode:
                if m_int_line_number == 0:
                    int_line_start = 0
                else:
                    int_line_start = m_int_line_number * self._int_avg_len - int(0.5 * self._int_avg_len)

                file.seek(int_line_start)
                if m_int_line_number != 0:
                    file.readline()
                return file.readline()
            else:
                dict_line_data = self._list_line_indexes[m_int_line_number]
                file.seek(dict_line_data['start'])
                return file.read(dict_line_data['length'])

    def get_lines(self, m_list_line_numbers):
        '''
        this method will recreive multiple lines from the text file
    
        Requirements:
        class FileSamplerBase
    
        Inputs:
        m_list_line_numbers
        Type: list
        Desc: integers of lines to retrieve
        
        Important Info:
        None
    
        Return:
        object
        Type: list
        Desc: strings represent the lines desired in text file
        '''
        if len(m_list_line_numbers) > self.number_of_lines:
            string_error = 'number of lines requested is more than the number of lines in the file;'
            string_error +=  'length of input list is too long'
            raise ValueError(string_error)

        list_return = list()

        for int_line in m_list_line_numbers:
            list_return.append(self.get_a_line(int_line))
        return list_return

    def get_random_lines(self, m_int_number_of_lines):
        '''
        this method will recreive random lines from the text file; this is random sampling with replacement
    
        Requirements:
        class FileSamplerBase
    
        Inputs:
        m_int_number_of_lines
        Type: int
        Desc: number of random lines to pull from file
        
        Important Info:
        None
    
        Return:
        object
        Type: list
        Desc: strings represent the lines desired in text file
        '''
        if m_int_number_of_lines > self.number_of_lines:
            raise ValueError('number of lines requested is more than the number of lines in the file')

        list_line_numbers = [randrange(0, self.number_of_lines) for x in range(0, m_int_number_of_lines)]
        return self.get_lines(list_line_numbers)

class CsvSampler(TextSampler):

    def __init__(self, m_string_filepath, m_bool_has_header = True,
                 m_bool_ignore_bad_lines = False, **kwargs):
        """
        :param filepath:
        :param has_header:
        :param kwargs: endline_character = '\n', values_delimiter = ',', 
        quotechar = '"', ignore_corrupt = False, ignore_blank_lines = True
        """
        super(TextSampler, self).__init__(m_string_filepath, 
            kwargs.get('m_string_endline_character','\n'), 
            kwargs.get('m_bool_estimate', False))
        self._tuple_header = None
        self._string_delimiter = kwargs.get('values_delimiter', ',')
        self._string_quotechar = kwargs.get('quotechar', '"')
        self._bool_has_header = m_bool_has_header
        self._bool_ignore_bad_lines = m_bool_ignore_bad_lines
        
        if has_header:
            self._tuple_header = self._csv_trans(self.get_a_line(0))

    @property
    def header(self):
        return self._tuple_header

    @property
    def has_header(self):
        return self._bool_has_header

    def _csv_trans(self, m_string_line):
        """
        this method supports the transition of the text line in the csv format
    
        Requirements:
        package MyDialect
        package csv
        package io.StringIO
    
        Inputs:
        m_string_line
        Type: string
        Desc: line to translate into a csv format
        
        Important Info:
        None
    
        Return:
        object
        Type: tuple
        Desc: line split into segments based on the dialect
        """
        dialect = self.MyDialect(self._string_endline, self._string_quotechar,
                    self._string_delimiter)
        b = StringIO(m_string_line)
        r = csv.reader(b, dialect)
        return tuple(next(r))

    def _parse_csv_values(self, m_string_line):
        """
        """
        values = self._csv_trans(m_string_line)
        if len(self._headers) != len(values):
            if not self._bool_ignore_bad_lines:
                raise ValueError("Corrupt csv - header and row have different lengths")
            return None
        return values

    def set_headers(self, header_list):
        if not hasattr(header_list, '__iter__'):
            raise TypeError("Argument 'header_list' must contain an iterable")
        self._headers = tuple(header_list)

    def get_a_csv_line(self, m_int_line_number):
        """
        """
        if self.has_header:
            m_int_line_number += 1
        
        string_line = self.get_a_line(m_int_line_number)
        tup_values = self._parse_csv_values(string_line)
        
        if self.has_header:
            return Series(data = tup_values, index = self.header)
        else:
            return Series(data = tup_values)

    def get_csv_lines(self, m_list_line_numbers):
        """
        """
        if len(m_list_line_numbers) > self.number_of_lines:
            string_error = 'number of lines requested is more than the number of lines in the file;'
            string_error +=  'length of input list is too long'
            raise ValueError(string_error)

        list_data = list()
        list_lines = self.get_lines(m_list_line_numbers)
        for string_line in list_lines:
            list_data.append(self._parse_csv_values(string_line))

        if self.has_header:
            return DataFrame(data = list_data, columns = self.header)
        else:
            return DataFrame(data = list_data)

    def get_csv_random_lines(self, m_int_num_lines):
        """
        """
        if m_int_num_lines > self.number_of_lines:
            raise ValueError('Number of lines requestes is greater than the number of lines in the file')

        list_line_numbers = [randrange(0, self.number_of_lines) for x in range(0, m_int_num_lines)]
        return self.get_csv_lines(list_line_numbers)

    class MyDialect(csv.Dialect):
        """
        """
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
