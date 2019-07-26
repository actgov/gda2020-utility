import pandas as pd
from time import gmtime, strftime
from datetime import datetime
from dateutil import tz
from os import listdir
from os.path import isfile, join
import shutil
import sys
import os

# Author: Aaron O'Hehir - actmapi administrator
# Date: 23/01/2018
# Details: Developed the extract_and_process_jurisdiction function
#
# Author: Joshua Thomson - SDMS project officer
# Date: 29/03/2018
# Details: Added convert_xyz_to_csv function to be used in fme
#
# Author: Aaron O'Hehir - actmapi administrator
# Date: 23/07/2019
# Details: Developed the fix_rinex_header function

""" 
    Creates a clean list where 
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
The purpose of this function is to fix the header of RINEX observation files.

"""

# gda2020.fix_rinex_header(   NGCA_observations_spreadsheet="Drive:\\Folder\\NGCA\\ACT NGCA Record.xlsx", \
#                             input_RINEX_directory="Drive:\\Folder\\NGCA\\20190722_ACT_NGCA_all RINEX files", \
#                             output_location_for_RINEX_directory="Drive:\\Folder\\NGCA")

def fix_rinex_header(NGCA_observations_spreadsheet, input_RINEX_directory, output_location_for_RINEX_directory):
    # Check to see if output directory exists
    # Delete output directory and sub files if it exists
    # Create empty output directory '20190722_ACT_NGCA_all RINEX files'. 
    # Change date and add Modified to end of folder name.
    # Store output location in variable
    date = str(datetime.today().strftime('%Y-%m-%d')).replace('-','')
    out_rinex_dir = os.path.join(output_location_for_RINEX_directory, date + '_ACT_NGCA_Modified')
    if os.path.isdir(out_rinex_dir) is True:
        shutil.rmtree(out_rinex_dir)
        os.makedirs(out_rinex_dir)
        os.makedirs(os.path.join(out_rinex_dir, 'log'))
    else:
        os.makedirs(out_rinex_dir)
        os.makedirs(os.path.join(out_rinex_dir, 'log'))
    
    # Create log file
    log_obj = open(os.path.join(out_rinex_dir, 'log', 'log.txt'), 'w')
    
    # Read in observations from NGCA spreadsheet
    xlsx = pd.ExcelFile(NGCA_observations_spreadsheet)
    # get the first sheet as an object
    sheet1 = xlsx.parse(0)
    
    ACT_NGCA_IDS = clean_input_list(sheet1.iloc[:,0].real)
    ACT_MARK_NAMES = clean_input_list(sheet1.iloc[:,2].real)
    RINEX_Filenames = clean_input_list(sheet1.iloc[:,9].real)
    
    # Read in a list of RINEX files in RIXEN directory
    RINEX_files = [f for f in listdir(input_RINEX_directory) if isfile(join(input_RINEX_directory, f))]
    
    # Create observation dict with 'ACT NGCA ID', 'ACT NAME' and 'RINEX_Filename' fields from observations spreadsheet
    # if 'ACT NGCA ID' is not nan and is a 4 character string that is number number alpha alpha
    # Iterate through RIXEN files and amending the header
    log_data = ''
    NGCA_observations = {}
    i = 0
    for act_ngca_id in ACT_NGCA_IDS:
        if (len(act_ngca_id) is 4):
            act_ngca_id = ACT_NGCA_IDS[i]
            act_mark_name = ACT_MARK_NAMES[i]
            RINEX_Filename = RINEX_Filenames[i]
            log_data += "NGCA: {0}, ACT Mark: {1}, RINEX: {2}\n".format(act_ngca_id, act_mark_name, RINEX_Filename)
            
            # Read RINEX file into a list
            rinex_to_open = os.path.join(input_RINEX_directory, RINEX_Filename)
            try:
                rinex_as_list = open(rinex_to_open).readlines()
            except IOError:
                log_data += 'No such file: ' + rinex_to_open + '\n'
            header_line_to_modify = rinex_as_list[4]
            # Modify the observation name from NGCA to ACT Mark Name
            if len(act_mark_name) is 3:
                replacement_line = act_mark_name + ' ' + header_line_to_modify[4:]
            else:
                replacement_line = act_mark_name + header_line_to_modify[len(act_mark_name):]
            rinex_as_list[4] = replacement_line
            
            # Write modified RINEX file to output location
            open(os.path.join(out_rinex_dir, RINEX_Filename), 'w').writelines(rinex_as_list)
            i += 1
        else:
            i += 1
    
    log_obj.write(log_data)

"""
    This function takes an input jurisdiction master list (xls document) and
    uses it to create a subset of the national adjustment (.xyz) file.
    The script also adopts (renames) jurisdiction mark names where there 
    is a conflict between NADJ and jurisdiction mark names.
    The jurisdiction xls has a column with NADJ mark names and another
    column containing jurisdiction mark names to adopt. 

    where:  jur_name = string name of jurisidiction.
            jur_marks_in = file name and extension to jurisdiction marks input xls file
            nadj_xyz_in = file name and extension to national adjustment input .xyz file
            nadj_apu_in = file name and extension to national adjustment input .apu file
            subset_out = path, file name and extension to jurisdiction subset output .xyz file
			input_dir = path to input directory which contains above input files
"""

# gda2020.extract_and_process_jurisdiction( jur_name="ACT", \
#                                           jur_marks_in="ACT_GDA2020_stn_master_list_20180131.xlsx", \
#                                           nadj_xyz_in="gda2020_20180131.phased-mt.xyz", \
#                                           nadj_apu_in="gda2020_20180131.phased-mt.apu", \
#                                           subset_out=r"Drive:/Path/To/Directory/GDA2020/output/stn_gda2020_20180131.xyz", \
#					                        input_dir = 'Drive:\\Path\\To\\Directory\\GDA2020\\input')

def extract_and_process_jurisdiction(jur_name, jur_marks_in, nadj_xyz_in, nadj_apu_in, subset_out, input_dir):
    
    """Process entrypoint"""
    python_dir = os.getcwd()

    jurisdiction_name = jur_name
    nadj_xyz_file = nadj_xyz_in
    nadj_apu_file = nadj_apu_in
    jurisdiction_input_file = jur_marks_in
    jurisdiction_output_file = subset_out

    os.chdir(input_dir)
    print(os.getcwd())

    # Create output file if it doesn't exist
    try:
        file = open(jurisdiction_output_file, 'r')
    except IOError:
        file = open(jurisdiction_output_file, 'w')
    
    # open national adjustment files
    xyz_file_obj = open(nadj_xyz_file, 'r')
    apu_file_obj = open(nadj_apu_file, 'r')
    # open act input xls
    xlsx = pd.ExcelFile(jurisdiction_input_file)
    # get the first sheet as an object
    sheet1 = xlsx.parse(0)

    os.chdir(python_dir)

    #parsed_national_survey_marks = sheet1.icol(0).real
    #parsed_jurisdiction_survey_marks = sheet1.icol(1).real
    parsed_national_survey_marks = sheet1.iloc[:,0].real
    parsed_jurisdiction_survey_marks = sheet1.iloc[:,1].real

    national_survey_marks = clean_input_list(parsed_national_survey_marks)
    jurisdiction_survey_marks = clean_input_list(parsed_jurisdiction_survey_marks)
    nadj_xyz_file_as_list = xyz_file_obj.readlines()
    nadj_apu_file_as_list = apu_file_obj.readlines()

    nadj_apu_dict = {}

    for mark_position_row in nadj_apu_file_as_list:
        raw_station_name = mark_position_row[:20]
        if raw_station_name != '                   ':
            raw_station_name = raw_station_name.rstrip()
            nadj_apu_dict[raw_station_name] = {"HzPosU": mark_position_row[56:62], "VzPosU": mark_position_row[67:73]}
    
    # Transfer metadata from national adjustment to output
    jurisdiction_marks_to_output = nadj_xyz_file_as_list[0:14]
    jurisdiction_marks_to_output = nadj_apu_file_as_list[0:12]
    jurisdiction_marks_to_output.append('EXTRACTION OF ' + jurisdiction_name + ' SURVEY CONTROL MARKS FROM NATIONAL GDA2020 ADJUSTMENT:\n')
    jurisdiction_marks_to_output.append('Input NADJ xyz file: ' + nadj_xyz_file + '\n')
    jurisdiction_marks_to_output.append('Input NADJ apu file: ' + nadj_apu_file + '\n')
    jurisdiction_marks_to_output.append('Input ' + jurisdiction_name + ' mark list: ' + jurisdiction_input_file + '\n')

    # Get time for metadata
    # Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcnow()
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)
    # Convert time zone
    aest = utc.astimezone(to_zone)
    date_str = "%d-%d-%d %d:%d:%d" % (aest.year, aest.month, aest.day, aest.hour, aest.minute, aest.second)

    jurisdiction_marks_to_output.append('Date-time Processed: ' + date_str + ' AEST\n')
    jurisdiction_marks_to_output.append('NOTES:\n')
    jurisdiction_marks_to_output.append('(1) h(Ellipse) = Height above the GRS80 ellipsoid.\n')
    jurisdiction_marks_to_output.append('(2) H(Ortho)   = Orthometric height (derived AHD)\n')
    jurisdiction_marks_to_output.append('\n')
    jur_stn_col_header = (jurisdiction_name + ' Station Name') + ' ' * 100
    nadj_xyz_file_as_list[18] = nadj_xyz_file_as_list[18].replace('Description', jur_stn_col_header[:20]).strip('\n')
    nadj_xyz_file_as_list[18] = nadj_xyz_file_as_list[18] + 'HzPosU    VzPosU    \n'
    
    jurisdiction_marks_to_output += nadj_xyz_file_as_list[15:20]

    for row_containing_mark in nadj_xyz_file_as_list[20:]:
        mark_name_nadj = row_containing_mark[:20].rstrip()
        for mark_name in national_survey_marks:
            if mark_name == mark_name_nadj and jurisdiction_survey_marks[national_survey_marks.index(mark_name)] != 'adopt_national_mark_name':
                jurisdiction_mark_name = jurisdiction_survey_marks[national_survey_marks.index(mark_name)] + (' ' * 100)
                jurisdiction_mark_name = jurisdiction_mark_name[:20]
                HzPosU = nadj_apu_dict[mark_name_nadj]["HzPosU"] + (' ' * 100)
                VzPosU = nadj_apu_dict[mark_name_nadj]["VzPosU"] + (' ' * 100)
                jurisdiction_marks_to_output.append(row_containing_mark[:192].strip('\n') + jurisdiction_mark_name + HzPosU[:10] + VzPosU[:10] + '\n')
            elif mark_name == mark_name_nadj and jurisdiction_survey_marks[national_survey_marks.index(mark_name)] == 'adopt_national_mark_name':
                national_mark_name = mark_name_nadj + (' ' * 100)
                national_mark_name = national_mark_name[:20]
                HzPosU = nadj_apu_dict[mark_name_nadj]["HzPosU"] + (' ' * 100)
                VzPosU = nadj_apu_dict[mark_name_nadj]["VzPosU"] + (' ' * 100)
                jurisdiction_marks_to_output.append(row_containing_mark[:192] + national_mark_name + HzPosU[:10] + VzPosU[:10] + '\n')

    jurisdiction_marks_to_output.append('------------------------    END    OF    REPORT   ------------------------\n')
    f = open(jurisdiction_output_file, 'r+')
    f.seek(0)
    f.writelines(jurisdiction_marks_to_output)
    f.truncate()
    f.close()


"""
    converts xyz file to csv file

"""

def convert_xyz_to_csv(in_file, out_file):

    out_file_obj = open(out_file, "a")
    list_of_lines = ['station,const,easting,northing,zone,latitude,longitude, \
                    h(ortho),h(ellipse),x,y,z,sd(e),sd(n),sd(up),act_station_name,hzposu,vzposu,\n']

    in_file_obj = open(in_file, "r")
    data = in_file_obj.readlines()[26:751]

    for line in data:
        station = line[0:20].rstrip()
        const = line[20:28].rstrip()
        easting = line[28:42].rstrip()
        northing = line[42:60].rstrip()
        zone = line[60:63].rstrip()
        latitude = line[63:78].rstrip()
        longitude = line[78:93].rstrip()
        hortho = line[93:104].rstrip().lstrip()
        hellipse = line[104:115].rstrip().lstrip()
        x = line[115:131].rstrip()
        y = line[131:145].rstrip()
        z = line[145:164].rstrip()
        sde = line[164:174].rstrip()
        sdn = line[174:184].rstrip()
        sdup = line[184:192].rstrip()
        description = line[192:212].rstrip()
        hzposu = line[212:222].rstrip()
        vzposu = line[222:232].rstrip()
        list_of_lines.append('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (station, const, easting, northing, zone, latitude, longitude, hortho, hellipse, x, y, z, sde, sdn, sdup, description, hzposu, vzposu))
    out_file_obj.writelines(list_of_lines)
    out_file_obj.close()
    return;
