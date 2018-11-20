import sys
import re
import argparse
import subprocess
import bam
import SURVIVORvcf
import annotateSURVIVOR

def parse_args():

	"""
	Parse command-line arguments

	Returns
	------

	Parser argument namespace
	"""

	parser = argparse.ArgumentParser(
			description="This script runs LUMPY, Manta, CNVnator, and ERDS"
			"on a bwa-mem aligned bam file." )
	parser.add_argument(
			"--bam_file", type=str, required=True,
			help="Path to bam file")
	parser.add_argument(
			"--reference", type=str, required=True,
			help="Path to reference fasta")
	parser.add_argument(
			"--chromosomes", type=str, required=True,
			help="Path to chromosome fastas")
	parser.add_argument(
		"--samtools_path", type=str, required=True,
		help="Path to Samtools executable")
	parser.add_argument(
		"--working_dir", type=str, required=True,
		help="Path to working directory")
	parser.add_argument(
		"--output_prefix", type=str, required=True,
		help="Output prefix for filenames, e.g. sample ID")
	#LUMPY-specific arguments
	parser.add_argument(
		"--lumpy_path", type=str, required=True,
		help="Path to LUMPY directory")
	parser.add_argument(
		"--lumpy", type=str, required=True,
		help="Path to LUMPY executable")
	parser.add_argument(
		"--read_length", type=str, required=True,
		help="Read length")
	parser.add_argument(
		"--min_mapq", type=str, required=True,
		help="Minimum mapping quality for running LUMPY")
	parser.add_argument(
		"--min_support", type=str, required=True,
		help="Minimum number of support reads for LUMPY call")
	#CNVnator-specific arguments
	parser.add_argument(
		"--CNVnator", type=str, required=True,
		help="Path to CNVnator exectuable")
	parser.add_argument(
		"--cnvnator2VCF", type=str, required=True,
		help="Path to cnvnator2VCF.pl script")
	parser.add_argument(
		"--bcftools", type=str, required=True,
		help="Path to bcftools exectuable")
	#Manta-specific arguments
	parser.add_argument(
		"--manta_config", type=str, required=True,
		help="path to configManta.py (i.e. (MANTA_INSTALL_PATH)/bin/configManta.py)")
	#ERDS-specific arguments
	parser.add_argument(
		"--ERDS_path", type=str, required=True,
		help="Path to erds_pipeline.pl")
	parser.add_argument(
		"--small_variant_vcf", type=str, required=True,
		help="Path to GATK SNV/indel vcf")
	#SURVIVOR-specific arguments
	parser.add_argument(
		"--SURVIVOR_path", type=str, required=True,
		help="Path to SURVIVOR executable")
	parser.add_argument(
		"--SURVIVOR_max_dist", type=str, required=True,
		help="Max distance between breakpoints")
	parser.add_argument(
		"--SURVIVOR_min_support", type=str, required=True,
		help="Minimum number of supporting callers")
	parser.add_argument(
		"--SURVIVOR_type", type=str, required=True,
		help="take the type into account (1=yes, 0=no)")
	parser.add_argument(
		"--SURVIVOR_strand", type=str, required=True,
		help="take the strands of SVs into account (1=yes, 0=no)")
	parser.add_argument(
		"--SURVIVOR_estimate_distance", type=str, required=True,
		help="estimate distance based on the size of SV (1=yes, 0=no)")
	parser.add_argument(
		"--SURVIVOR_min_SV", type=str, required=True,
		help="minimum size of SVs to be taken into account")
	parser.add_argument(
		"--SURVIVOR_additional_vcfs", nargs='+', required=False,
		help="additional SV vcfs to input to SURVIVOR")
	#Annovar-specific arguments
	parser.add_argument(
		"--table_annovar", type=str, required=True,
		help="path to Annovar table_annovar.pl script")
	parser.add_argument(
		"--humandb", type=str, required=True,
		help="path to Annovar humandb/ folder containing annotations of interest")
	parser.add_argument(
		"--annovar_reference", type=str, required=True,
		help="hg19 or hg38")
	parser.add_argument(
		"--deletion_bedfiles", required=True, nargs='+', help="A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, the minimum fraction of overlap of the sample SV with region of interest is the third element, the fourth element is TRUE if it is desired to have the percentage overlap of the database annotation calculated, otherwise FALSE, and the fifth element is the name of the annotation  (e.g. 'gene_promoters.bed, 4, 0.9, TRUE, Gene_promoters'")
	parser.add_argument(
		"--duplication_bedfiles", required=True, nargs='+', help="A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, the minimum fraction of overlap of the sample SV with region of interest is the third element,the fourth element is TRUE if it is desired to have the percentage overlap of the database annotation calculated, otherwise FALSE, and the fifth element is the name of the annotation  (e.g. 'gene_promoters.bed, 4, 0.9, TRUE, Gene_promoters'")
	parser.add_argument(
		"--inversion_bedfiles", required=True, nargs='+', help="A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, the minimum fraction of overlap of the sample SV with region of interest is the third element,the fourth element is TRUE if it is desired to have the percentage overlap of the database annotation calculated, otherwise FALSE, and the fifth element is the name of the annotation  (e.g. 'gene_promoters.bed, 4, 0.9, TRUE, Gene_promoters'")
	parser.add_argument(
		"--insertion_bedfiles", required=True, nargs='+', help="A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, the minimum fraction of overlap of the sample SV with region of interest is the third element,the fourth element is TRUE if it is desired to have the percentage overlap of the database annotation calculated, otherwise FALSE, and the fifth element is the name of the annotation  (e.g. 'gene_promoters.bed, 4, 0.9, TRUE, Gene_promoters'")
	parser.add_argument(
		"--breakend_bedfiles", required=True, nargs='+', help="A list where the file name of regions of interest in bed format is the first element, an integer specifiying the column of interest for annotation is the second element, the minimum fraction of overlap of the sample SV with region of interest is the third element, the fourth element is TRUE if it is desired to have the percentage overlap of the database annotation calculated, otherwise FALSE, and the fifth element is the name of the annotation  (e.g. 'gene_promoters.bed, 4, 0.9, TRUE, Gene_promoters'")



	args = parser.parse_args()
	return args

def main():
	args = parse_args()

	command_line = "mkdir {}".format(args.working_dir)
	subprocess.call(command_line, shell=True)

	#instantiate bam object
	sample_bam = bam.bam_file(args.bam_file, args.reference, args.samtools_path)

	#Extract and sort discordant and split reads
	sample_bam.extract_discordants(args.working_dir, args.output_prefix)
	sample_bam.extract_splitters(args.lumpy_path, args.working_dir, args.output_prefix)
	discordants = args.working_dir + '/' + args.output_prefix + ".discordants.unsorted.bam"
	splitters = args.working_dir + '/' + args.output_prefix + ".splitters.unsorted.bam"
	splitters_sorted = args.output_prefix + ".splitters"
	discordants_sorted = args.output_prefix + ".discordants"
	sample_bam.sort_bam(splitters, args.working_dir, splitters_sorted)
	sample_bam.sort_bam(discordants, args.working_dir, discordants_sorted)

	#Run LUMPY
	LUMPY = sample_bam.run_LUMPY(args.lumpy, args.working_dir, args.output_prefix,
		sample_bam.get_insert_size(args.lumpy_path, args.working_dir, args.output_prefix), args.read_length, args.min_mapq, args.min_support)

	#Run CNVnator
	CNVnator = sample_bam.run_CNVnator(args.CNVnator, args.cnvnator2VCF, args.bcftools, args.chromosomes, args.working_dir, args.output_prefix)

	#Generate Manta config file, then run Manta
	Manta_Dir = sample_bam.Manta_config(args.manta_config, args.working_dir, args.output_prefix)
	Manta = sample_bam.run_Manta(Manta_Dir)

	#Run ERDS
	ERDS = sample_bam.run_ERDS(args.ERDS_path, args.working_dir, args.output_prefix, args.small_variant_vcf)


	#Generate list of SV vcfs, then run SURVIVOR
	if  args.SURVIVOR_additional_vcfs != None:
		variant_list = sample_bam.make_variant_file(args.working_dir, args.output_prefix, LUMPY, CNVnator, Manta, ERDS, args.SURVIVOR_additional_vcfs)
	else:
		variant_list = sample_bam.make_variant_file(args.working_dir, args.output_prefix, LUMPY, CNVnator, Manta, ERDS)
	
	SURVIVOR = sample_bam.run_SURVIVOR(args.SURVIVOR_path, variant_list,
	args.SURVIVOR_max_dist, args.SURVIVOR_min_support,
	args.SURVIVOR_type, args.SURVIVOR_strand, args.SURVIVOR_estimate_distance, args.SURVIVOR_min_SV, args.working_dir, args.output_prefix)

	#Convert SURIVIVOR vcf to avinput
	SURVIVOR = SURVIVORvcf.SURVIVOR_vcf(SURVIVOR)
	avinput = SURVIVOR.SURVIVOR_to_avinput(args.output_prefix, args.working_dir)
	
	#Separate SVs by type (ie DEL, DUP, INS, INV, BND)
	annotateSURVIVOR.split_by_SV_type(avinput, args.output_prefix, args.working_dir)
	DEL = args.working_dir + "/" +  args.output_prefix + ".DEL"
	DUP = args.working_dir +  "/" + args.output_prefix + ".DUP"
	INV = args.working_dir +  "/" + args.output_prefix + ".INV"
	INS = args.working_dir +  "/" + args.output_prefix + ".INS"
	BND = args.working_dir +  "/" + args.output_prefix + ".BND"

	#Annotate variants
	annotated_DEL = annotateSURVIVOR.annotate_avinput(DEL, args.table_annovar, args.humandb, args.annovar_reference, args.output_prefix + ".DEL", args.working_dir, args.deletion_bedfiles) 

	annotated_DUP = annotateSURVIVOR.annotate_avinput(DUP, args.table_annovar, args.humandb, args.annovar_reference, args.output_prefix + ".DUP", args.working_dir, args.duplication_bedfiles) 

	annotated_INV = annotateSURVIVOR.annotate_avinput(INV, args.table_annovar, args.humandb, args.annovar_reference, args.output_prefix + ".INV", args.working_dir, args.inversion_bedfiles) 

	annotated_INS = annotateSURVIVOR.annotate_avinput(INS, args.table_annovar, args.humandb, args.annovar_reference, args.output_prefix + ".INS", args.working_dir, args.insertion_bedfiles) 

	annotated_BND = annotateSURVIVOR.annotate_avinput(BND, args.table_annovar, args.humandb, args.annovar_reference, args.output_prefix + ".BND", args.working_dir, args.breakend_bedfiles) 

	#Calculate reciprocal overlap for specified bed files
	annotated_DEL_overlap = annotateSURVIVOR.calculate_overlap(args.output_prefix, args.working_dir, annotated_DEL, "DEL",  args.deletion_bedfiles)

	annotated_DUP_overlap = annotateSURVIVOR.calculate_overlap(args.output_prefix, args.working_dir,annotated_DUP, "DUP",  args.duplication_bedfiles)

	annotated_INV_overlap = annotateSURVIVOR.calculate_overlap(args.output_prefix, args.working_dir,annotated_INV, "INV",  args.inversion_bedfiles)

	annotated_INS_overlap = annotateSURVIVOR.calculate_overlap(args.output_prefix, args.working_dir,annotated_INS, "INS",  args.insertion_bedfiles)

	annotated_BND_overlap = annotateSURVIVOR.calculate_overlap(args.output_prefix, args.working_dir,annotated_BND, "BND",  args.breakend_bedfiles)

	#Add headers
	#Deletion
	DEL_header = annotateSURVIVOR.add_header(args.output_prefix, args.working_dir, "DEL",  args.deletion_bedfiles)

	command_line = "cat {} {} > {} ".format(DEL_header, annotated_DEL_overlap, args.working_dir + "/" +  args.output_prefix + ".DEL" + ".withoverlap.header.annovar.hg19_multianno.txt")
	subprocess.call(command_line, shell=True) 

	#Duplication
	DUP_header = annotateSURVIVOR.add_header(args.output_prefix, args.working_dir, "DUP",  args.duplication_bedfiles)

	command_line = "cat {} {} > {} ".format(DUP_header, annotated_DUP_overlap, args.working_dir + "/" + args.output_prefix + ".DUP" + ".withoverlap.header.annovar.hg19_multianno.txt")
	subprocess.call(command_line, shell=True)

	#Inversion
	INV_header = annotateSURVIVOR.add_header(args.output_prefix, args.working_dir, "INV",  args.inversion_bedfiles)

	command_line = "cat {} {} > {} ".format(INV_header, annotated_INV_overlap, args.working_dir + "/" + args.output_prefix + ".INV" + ".withoverlap.header.annovar.hg19_multianno.txt")
	subprocess.call(command_line, shell=True)

	#Insertion
	INS_header = annotateSURVIVOR.add_header(args.output_prefix, args.working_dir, "INS",  args.insertion_bedfiles)

	command_line = "cat {} {} > {} ".format(INS_header, annotated_INS_overlap, args.working_dir + "/" + args.output_prefix + ".INS" + ".withoverlap.header.annovar.hg19_multianno.txt")
	subprocess.call(command_line, shell=True)

	#Breakend
	BND_header = annotateSURVIVOR.add_header(args.output_prefix, args.working_dir, "BND",  args.breakend_bedfiles)

	command_line = "cat {} {} > {} ".format(BND_header, annotated_BND_overlap, args.working_dir + "/" + args.output_prefix + ".BND" + ".withoverlap.header.annovar.hg19_multianno.txt")
	subprocess.call(command_line, shell=True)


main()
