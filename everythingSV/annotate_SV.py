import sys
import re
import os
import subprocess
import argparse

def parse_args():

	"""
	Parse command-line arguments

	Returns
	------

	Parser argument namespace
	"""

    parser = argparse.ArgumentParser(
        description="This script annotates a set of SVs in avinput."
    )
    parser.add_argument(
        "--table_annovar", type=str, required=True, help="path to Annovar table_annovar.pl script"
    )
    parser.add_argument(
        "--humandb", type=str, required=True, help="path to humandb/ folder containing annotations of interest"
    )
    parser.add_argument(
        "--reference", type=str, required=True, help="hg19 or hg38"
    )
    parser.add_argument(
        "--output_prefix", type=str, required=True, help="sample prefix"
    )
    parser.add_argument(
        "--workdir", type=str, required=True, help="working directory (output is written here)"
    )
    parser.add_argument(
        "--bedfiles", type=list, required=True, help="A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, and the minimum fraction of overlap of sample SV with region of interest is the third element (e.g. 'gene_promoters.bed, 4, 0.9')"
    )
    parser.add_argument()

def annotate_avinput(self, table_annovar, humandb, reference, output_prefix, workdir, *bedfiles):
    """
    Annotates a set of structural variants in avinput format

    Parameters
    ----------

    table_annovar : str
        path to table_annovar.pl script

    humandb : str
        path to humandb/ folder containing annotations of interest

    reference : str
        hg19 or hg38

    bed_file : str
        regions of interest in bed format

    cols_wanted : int
        column number for annotation of interest

    minqueryfrac : float
        minimum fraction of overlap of sample SV with region of interest for annotation

    output_prefix : str
        sample prefix

    workdir : str
        working directory (output is written here)

    bedfiles : list
        A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, and the minimum fraction of overlap of sample SV with region of interest is the third element (e.g. "gene_promoters.bed, 4, 0.9")

    cols_wanted : int
        column number for annotation of interest

    minqueryfrac : float
        minimum fraction of overlap of sample SV with region of interest for annotation

    Returns
    -------

    str
        path to annotated SV text file

    Raises
    ------

    To do!

    """
    protocols = ""
    filenames = ""
    operations = ""
    bed_args = ""
    num_files = len(bedfiles)

    #Iterate through bed files to extract filenames, protocol, and operation for input to Annovar
    for bedfile in bedfiles:
        if num_files > 1:
            bedfile = bedfile.strip('').split(",")
            filenames = filenames + bedfile[0] + ","
            cols = str(bedfile[1])
            frac = str(bedfile[2])
            print cols
            print frac
            if "NA" in cols:
                print cols
                if "NA" not in frac:
                    bed_args = bed_args + " -minqueryfrac "  + frac + ","
                else:
                    bed_args = bed_args + ","
            elif "NA" not in frac:
                bed_args = bed_args + "-colsWanted " + cols + " -minqueryfrac "  + frac + ","
            else:
                bed_args = bed_args + "-colsWanted " + cols + ","
            protocols = protocols + "bed,"
            operations = operations + "r,"
            num_files = num_files - 1
        else:
            bedfile = bedfile.strip('').split(",")
            filenames = filenames + bedfile[0]
            cols = bedfile[1]
            frac = bedfile[2]
            if "NA" in cols:
                print cols
                if "NA" not in frac:
                    bed_args = bed_args + " -minqueryfrac "  + frac
                else:
                    bed_args = bed_args + ""
            elif "NA" not in frac:
                bed_args = bed_args + "-colsWanted " + cols + " -minqueryfrac "  + frac
            else:
                bed_args = bed_args + "-colsWanted " + cols
            protocols = protocols + "bed"
            operations = operations + "r"
            num_files = num_files - 1


    command_line = "perl {} {} {} -buildver {} -out {} -nastring . -remove -otherinfo -protocol {} -bedfile {} -operation {} -arg '{}' ".format(
        table_annovar, self.file_path, humandb, reference, workdir + '/' +
        output_prefix + '.annovar.txt', protocols, filenames, operations, bed_args)

    print command_line

    subprocess.call(command_line, shell=True)

    return command_line