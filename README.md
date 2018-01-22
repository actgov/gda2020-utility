# gda2020-utility

Description:

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
