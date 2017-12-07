from FileSamplerRandom import CsvRandomAccessReader
from FileSamplerRandom import RandomAccessReader
import os
import random
import pandas
from Timer import Timer

string_file_air = os.path.abspath('../../../../Education/MS Data Science/Quantifying the World/Project 12/Data/all_data.csv')
string_path_data = os.path.abspath('../tests')
string_csv_file_00 = 'test_file.csv'
string_file_01 = 'test_file_01.txt'

timer_test = Timer()
#txt_reader = RandomAccessReader(os.path.join(string_path_data, string_file_01))
csv_reader = CsvRandomAccessReader(string_file_air)
#print('header', csv_reader.headers)
#list_random_lines = random.sample(range(0, csv_reader.number_of_lines), 100000)

#list_lines = list()
#for int_line in list_random_lines:
#    list_lines.append(csv_reader.get_line_dicts(int_line))
#print(list_lines)

df_temp = pandas.DataFrame(data = csv_reader.get_sample(100000), 
                           columns = csv_reader.headers)
timer_test.stop_timer('100k test')
print('stop')

#list_lines_txt = txt_reader.get_lines(0)
#list_lines = csv_reader.get_line_dicts(3, 3)