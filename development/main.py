from FileSamplerRandom import CsvRandomAccessReader
from FileSamplerRandom import RandomAccessReader
import os

string_file_air = '~/Documents/Education/MS Data Science/Quantifying the World/Project 12/Data/'
string_file_air += 'all_data.csv'
string_path_data = os.path.abspath('../tests')
string_csv_file_00 = 'test_file.csv'
string_file_01 = 'test_file_01.txt'

#txt_reader = RandomAccessReader(os.path.join(string_path_data, string_file_01))
csv_reader = CsvRandomAccessReader(os.path.abspath(string_file_air))

#list_lines_txt = txt_reader.get_lines(0)
list_lines = csv_reader.get_line_dicts(3, 3)