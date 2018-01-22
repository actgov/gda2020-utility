import pandas as pd
from time import gmtime, strftime
import argparse
import sys

# Author: Aaron O'Hehir - actmapi administrator
# Date: 22/01/2018

""" Creates a clean list where 
    unicode strings are converted to ascii,
    nan and int are converted to strings.
"""
def clean_input_list(mark_list):
    cleaned_list = []
    for mark in mark_list:
        if type(mark) is float:
            cleaned_list.append('adopt_national_mark_name')
        elif type(mark) is unicode:
            cleaned_list.append(mark.encode('ascii'))
        elif type(mark) is int:
            cleaned_list.append(str(mark))
    return cleaned_list

"""
    This script takes an input jurisdiction master list (xls document) and
    uses it to create a subset of the national adjustment (.xyz) file.
    The script also adopts (renames) jurisdiction mark names where there 
    is a conflict between NADJ and jurisdiction mark names.
    The jurisdiction xls has a column with NADJ mark names and another
    column containing jurisdiction mark names to adopt. 

    Sample Usage: python gda2020_utility.py --jurisdiction_marks_in Drive:\path\jurisdiction_marks_in.xls 
                                            --national_marks_in Drive:\path\national_marks_in.xyz 
                                            --subset_out Drive:\path\subset_out.xyz

    where:  jurisdiction_marks_in = path, file name and extension to jurisdiction marks input xls file
            national_marks_in = path, file name and extension to national adjustment input .xyz file
            subset_out = path, file name and extension to jurisdiction subset output .xyz file
"""

def main():
    """Process entrypoint"""
    parser = argparse.ArgumentParser(description='Create jurisdiction subset from national marks list')
    parser.add_argument('--jurisdiction_marks_in', help='input jurisdiction marks file', type=str, required=True)
    parser.add_argument('--national_marks_in', help='Input national adjustment file', type=str, required=True)
    parser.add_argument('--subset_out', help='path, file name and extension to write subset results to.', type=str, required=True)
    args = parser.parse_args()

    jurisdiction_input_file = args.jurisdiction_marks_in
    national_input_file = args.national_marks_in
    jurisdiction_output_file = args.subset_out

    # Create output file if it doesn't exist
    try:
        file = open(jurisdiction_output_file, 'r')
    except IOError:
        file = open(jurisdiction_output_file, 'w')
    
    # open act input xls
    xlsx = pd.ExcelFile(jurisdiction_input_file)
    # get the first sheet as an object
    sheet1 = xlsx.parse(0)
    # open national adjustment list
    f = open(national_input_file, 'r')

    parsed_national_survey_marks = sheet1.icol(0).real
    parsed_act_survey_marks = sheet1.icol(1).real

    national_survey_marks = clean_input_list(parsed_national_survey_marks)
    act_survey_marks = clean_input_list(parsed_act_survey_marks)
    national_input_file_as_list = f.readlines()

    # Transfer metadata from national adjustment to output
    act_marks_to_output = national_input_file_as_list[0:14]
    act_marks_to_output.append('Input NADJ file: ' + national_input_file + '\n')
    act_marks_to_output.append('Input Jurisdiction mark list: ' + jurisdiction_input_file + '\n')
    act_marks_to_output.append('Date Processed: ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '\n')
    act_marks_to_output.append('\n')
    act_marks_to_output += national_input_file_as_list[15:20]

    for row_containing_mark in national_input_file_as_list[20:]:
        mark_name_nadj = row_containing_mark[:20].rstrip()
        for mark_name in national_survey_marks:
            if mark_name == mark_name_nadj and act_survey_marks[national_survey_marks.index(mark_name)] != 'adopt_national_mark_name':
                adopted_mark_name = act_survey_marks[national_survey_marks.index(mark_name)] + (' ' * 50)
                adopted_mark_name = adopted_mark_name[:20]
                act_marks_to_output.append(adopted_mark_name + row_containing_mark[20:])
            elif mark_name == mark_name_nadj and act_survey_marks[national_survey_marks.index(mark_name)] == 'adopt_national_mark_name':
                act_marks_to_output.append(row_containing_mark)
    f = open(jurisdiction_output_file, 'r+')
    f.seek(0)
    f.writelines(act_marks_to_output)
    f.truncate()
    f.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(1)