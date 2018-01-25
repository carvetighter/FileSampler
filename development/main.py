from FileSampler import TextSampler
from FileSampler import CsvSampler
from FileSampler import FileSamplerBase
import os
import random
import pandas
from Timer import Timer

#string_file_air = os.path.abspath('../../../../Education/MS Data Science/Quantifying the World/Project 12/Data/all_data.csv')
string_path_data = os.path.abspath('../tests')
string_csv_file_00 = 'test_file.csv'
string_file_01 = 'test_file_01.txt'

timer_test = Timer()
#fsb = FileSamplerBase(os.path.join(string_path_data, string_file_01), '\n', False)
#txt_reader = TextSampler(os.path.join(string_path_data, string_file_01))

csv_reader = CsvSampler(os.path.join(string_path_data, string_csv_file_00))
#print('header', csv_reader.headers)
#list_random_lines = random.sample(range(0, csv_reader.number_of_lines), 100000)

#list_lines = list()
#for int_line in list_random_lines:
#    list_lines.append(csv_reader.get_line_dicts(int_line))
#print(list_lines)

df_temp = pandas.DataFrame(data = csv_reader.get_csv_random_lines(10), columns = csv_reader.header)
timer_test.stop_timer('10 test')
#print(df_temp.iloc[0])

#list_lines_txt = txt_reader.get_lines(0)
#list_lines = csv_reader.get_line_dicts(3, 3)