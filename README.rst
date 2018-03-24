File Sampler
-------------------------

| This is a small library that allows for reading any given line in a file without having to read all the lines before it
  or load the entire file into memory.  Only the line indexes and lengths are held in memory, which enables random
  access even on very large files for a very minuscule memory cost.

Installation
============
``pip install FileSampler``

Usage
=====

| Usage is very straightforward, and standard csv line endings (newline character), value delimiter (comma), and
  quotation character (double quote) are the defaults.  These can be changed in the constructor.
|
| The ``get_line()`` method returns a string which represents one row.
| The ``get_lines()`` methods returns a list of strings which represents multiple rows.
| The '``get_random_lines()`` method returns a list of stirngs that represents multple rows
| selected randomly.
|
| **Plain text file example:**

::

    from FileSampler import TextSampler

    sampler_text = TextSampler('c:\file path\text_file.txt')

    # single line
    string_line = sampler_text.get_a_line(int_line_number)
    print(string_line)

    # multiple lines
    list_lines = sampler_text.get_lines(list_line_numbers)
    for line in list_lines:
        print(line)

    # random lines
    list_random_lines = sampler_text.get_random_lines(int_number_of_random_lines)
    for line in list_random_lines:
        print(line)

| Optional arguments in the constructor:

- ``m_string_endline_character`` - self-explanatory (default is endline character ``\n``)
- ``m_bool_estimate`` - if set to ``True``, blank lines in the file will not be read or indexed (default is ``False``)

|
| Each instance of a TextSampler or CsvSamper class has the properies:

- ``number_of_lines`` -> type: int; returns the number of lines in the file
- ``estimate_mode`` -> type: bool; flag if the class counted all the line lenghts in the
file or estimated the line length based on a sample

|
| Each instance of a CsvSampler has the following properties and is desing to sample csv
| formatted text files.
|
| CsvSampler Properteis:
- ``header``: returns the header of the csv file if there is one in the form of a tuple of strings
- ``has_header``: a boolean flag which returns True or False if a header exists

|
| **Csv example:**

::

    from FileSampler import CsvSampler
    sampler_csv = CsvSampler('~/myfile.csv')
    

    # single line
    series_line = sampler_csv.get_a_csv_line(int_line_number)
    # returns a pandas Series with the; the index is the header of it exists

    # multiple lines
    df_lines = sampler_csv.get_csv_lines(list_line_numbers)
    for string_column in df_lines:
        for int_line in range(0, len(df_lines)):
            print(df_lines[string_column].iloc[int_line])
    # returns a pandas DataFrame where the columns are the file headers; the above example will
    # print each line of each column in the dataframe

    # random lines
    df_random_lines = sampler_csv.get_csv_random_lines(int_number_of_random_lines)
    for int_line in range(0, len(df_random_lines)):
        print(df_random_lines.iloc[int_line])
    # returns a pandas DataFrame whre the columns are the header of it exists
    # the above example prints each full line of the csv file


| Optional arguments in the constructor in addition to TextSampler agruments:

- ``m_bool_ignore_bad_lines`` - if set to ``True``, lines that do not fit the csv file format will be ignored (default is ``False``)
- ``string_values_delimiter`` - character used by the csv to separate values within a line (default is ``,``)
- ``string_quotechar`` - character used by the csv to surround values that contain the value delimiting character (default is ``"``)
- ``m_bool_has_header`` - if set to ``True``, the first line of the csv file will be used at the header / column names for the DataFrame (default is ``True``)