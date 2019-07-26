# gda2020-utility

Description:

This script contains three functions which are used in the preperation 
and processing of GDA2020 survey mark observations.

gda2020.fix_rinex_header()
    
    This function amends the header of the RINEX survey mark observation file.
    The RINEX files are processed by Geoscience Australia and have Commonwealth 
    mark ids in the form of Number Number Alpha Alpha. This scripts uses the 
    ACT NGCA Record.xlsx spreadsheet to map the ACT mark names and then rename 
    the Commonwealth ids int he RINEX header files.

gda2020.extract_and_process_jurisdiction()

    This function takes an input jurisdiction master list (xls document) and
    uses it to create a subset of the national adjustment (.xyz) file.
    The script also adopts (renames) jurisdiction mark names where there 
    is a conflict between NADJ and jurisdiction mark names.
    The jurisdiction xls has a column with NADJ mark names and another
    column containing jurisdiction mark names to adopt. 
 
gda2020.convert_xyz_to_csv()
    
    This function converts the output xyz file to csv. The function is called 
    from an FME workbench. The purpose is to prepare the data for ingestion 
    into the ACTmapi survey infrastructure site.
    http://app.actmapi.act.gov.au/actmapi/index.html?viewer=scm
