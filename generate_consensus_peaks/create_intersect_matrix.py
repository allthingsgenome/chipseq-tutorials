#!/usr/bin/env python3

"""
Title: Create intersection matrix from merged peak file
Author: Carlos Guzman
Date: March 20, 2024
Description:
    This script takes a merged peak file from MACS2 and optional parameters, and generates
    an output file that contains additional information about the merged peaks and their
    presence or absence in each sample. It also creates a separate file that summarizes the
    unique combinations of samples present in the merged broad peaks, which can be used for
    further analysis or visualization.
Usage:
    python create_intersect_matrix.py <MERGED_INTERVAL_FILE> <OUTFILE> [--min_replicates MIN_REPLICATES]
Arguments:
    MERGED_INTERVAL_FILE: Merged MACS2 interval file created using linux sort and mergeBed for broad peaks.
    OUTFILE: Full path to the output file.
    --min_replicates MIN_REPLICATES (optional): Minimum number of replicates per sample required to contribute to a merged broad peak (default: 1).
Example:
    python create_intersect_matrix.py merged_broad_peaks.txt output.txt --min_replicates 1
"""

import os
import errno
import argparse

############################################
# PARSE ARGUMENTS
############################################

Description = "Add sample boolean files and aggregate columns from merged MACS peak file."
argParser = argparse.ArgumentParser(description=Description)

# REQUIRED PARAMETERS
argParser.add_argument("MERGED_INTERVAL_FILE", help="Merged MACS2 interval file created using linux sort and mergeBed for peaks.")
argParser.add_argument("OUTFILE", help="Full path to output file.")

# OPTIONAL PARAMETERS
argParser.add_argument("-mr", "--min_replicates", type=int, dest="MIN_REPLICATES", default=1, help="Minimum number of replicates per sample required to contribute to merged peak (default: 1).")

args = argParser.parse_args()

############################################
# HELPER FUNCTIONS
############################################

def makedir(path):
    """
    Create a directory if it doesn't exist.

    Args:
        path (str): The path to the directory.

    Raises:
        OSError: If the directory cannot be created and the error is not because the directory already exists.
    """
    if not len(path) == 0:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

############################################
# MAIN FUNCTION
############################################

def macs2_merged_expand(merged_interval_file, outfile, min_replicates=1):
    """
    Process and merge information from multiple broad peak files generated by the MACS2 peak caller tool.

    Args:
        merged_interval_file (str): The path to the merged interval file (created by sorting and merging individual MACS2 broad peak files).
        outfile (str): The path to the output file.
        min_replicates (int, optional): The minimum number of replicates per sample required to contribute to a merged peak. Defaults to 1.

    Notes:
        - The merged interval file is assumed to be created using the following command:
          sort -k1,1 -k2,2n *.narrowPeak | mergeBed -c 2,3,4,5,6,7,8,9 -o collapse,collapse,collapse,collapse,collapse,collapse,collapse,collapse > merged_peaks.txt
        - The output file contains additional information about the merged broad peaks and their presence or absence in each sample.
        - An additional file (with the extension ".intersect.txt") is created, which contains the unique combinations of samples and their frequencies, sorted in descending order. This file is compatible with the UpSetR package for visualizing set intersections.
    """
    makedir(os.path.dirname(outfile))

    # Initialize dictionaries
    comb_freq_dict = {}  # To store the frequency of unique combinations of samples present in each merged peak region
    total_out_intervals = 0  # To keep track of the total number of output intervals

    # Collect all unique sample names from the merged interval file
    # This part doesn't generalize very well because it splits the sample names based on the first instance of "." which may not be the case for peak files created outside our pipeline
    all_sample_names = set()
    with open(merged_interval_file, "r") as fin:
        for line in fin:
            lspl = line.strip().split("\t")
            names = lspl[5].split(",")
            all_sample_names.update([name.split(".")[0].split("_peak_")[0] for name in names])

    # Sort the sample names for consistent ordering
    sample_name_list = sorted(all_sample_names)

    # Open input and output files
    with open(merged_interval_file, "r") as fin, open(outfile, "w") as fout:
        # Define output header fields
        ofields = ["chr", "start", "end", "interval_id", "num_peaks", "num_samples"] + \
                  [f"{x}.bool" for x in sample_name_list] + \
                  [f"{x}.fc" for x in sample_name_list] + \
                  [f"{x}.qval" for x in sample_name_list] + \
                  [f"{x}.pval" for x in sample_name_list] + \
                  [f"{x}.start" for x in sample_name_list] + \
                  [f"{x}.end" for x in sample_name_list]

        # Write output header
        fout.write("\t".join(ofields) + "\n")

        # Process each line in the input file
        for line in fin:
            lspl = line.strip().split("\t")

            chrom_id = lspl[0]
            mstart = int(lspl[1])
            mend = int(lspl[2])
            starts = [int(x) for x in lspl[3].split(",")]
            ends = [int(x) for x in lspl[4].split(",")]
            names = lspl[5].split(",")
            fcs = [float(x) for x in lspl[8].split(",")]
            pvals = [float(x) for x in lspl[9].split(",")]
            qvals = [float(x) for x in lspl[10].split(",")]

            # GROUP SAMPLES BY REMOVING TRAILING *_peak_*
            group_dict = {}
            for sid in [name.split(".")[0].split("_peak_")[0] for name in names]:
                gid = "_".join(sid.split("_")[:-1])
                if gid not in group_dict:
                    group_dict[gid] = []
                if sid not in group_dict[gid]:
                    group_dict[gid].append(sid)

            # GET SAMPLES THAT PASS REPLICATE THRESHOLD
            pass_rep_thresh_list = []
            for gid, sids in group_dict.items():
                if len(sids) >= min_replicates:
                    pass_rep_thresh_list += sids

            # GET VALUES FROM INDIVIDUAL PEAK SETS
            fc_dict = {}
            qval_dict = {}
            pval_dict = {}
            start_dict = {}
            end_dict = {}
            for idx in range(len(names)):
                sample = names[idx].split(".")[0].split("_peak_")[0]
                if sample in pass_rep_thresh_list:
                    if sample not in fc_dict:
                        fc_dict[sample] = []
                    fc_dict[sample].append(str(fcs[idx]))
                    if sample not in qval_dict:
                        qval_dict[sample] = []
                    qval_dict[sample].append(str(qvals[idx]))
                    if sample not in pval_dict:
                        pval_dict[sample] = []
                    pval_dict[sample].append(str(pvals[idx]))
                    if sample not in start_dict:
                        start_dict[sample] = []
                    start_dict[sample].append(str(starts[idx]))
                    if sample not in end_dict:
                        end_dict[sample] = []
                    end_dict[sample].append(str(ends[idx]))

            # Construct and write output line
            samples = sorted(fc_dict.keys())
            if samples:
                num_samples = len(samples)
                bool_list = ["TRUE" if x in samples else "FALSE" for x in sample_name_list]
                fc_list = [";".join(fc_dict[x]) if x in samples else "NA" for x in sample_name_list]
                qval_list = [";".join(qval_dict[x]) if x in samples else "NA" for x in sample_name_list]
                pval_list = [";".join(pval_dict[x]) if x in samples else "NA" for x in sample_name_list]
                start_list = [";".join(start_dict[x]) if x in samples else "NA" for x in sample_name_list]
                end_list = [";".join(end_dict[x]) if x in samples else "NA" for x in sample_name_list]
                olist = [str(x) for x in [chrom_id, mstart, mend, f"Interval_{total_out_intervals + 1}", len(names), num_samples]] + \
                        bool_list + fc_list + qval_list + pval_list + start_list + end_list
                fout.write("\t".join(olist) + "\n")

                tsamples = tuple(sorted(samples))
                if tsamples not in comb_freq_dict:
                    comb_freq_dict[tsamples] = 0
                comb_freq_dict[tsamples] += 1
                total_out_intervals += 1

    # WRITE FILE FOR INTERVAL INTERSECT ACROSS SAMPLES
    # COMPATIBLE WITH UPSETR PACKAGE
    with open(f"{outfile[:-4]}.intersect.txt", "w") as fout:
        comb_freq_items = sorted([(comb_freq_dict[x], x) for x in comb_freq_dict.keys()], reverse=True)
        for k, v in comb_freq_items:
            fout.write("%s\t%s\n" % ("&".join(v), k))

############################################
# RUN FUNCTION
############################################

macs2_merged_expand(
    merged_interval_file=args.MERGED_INTERVAL_FILE,
    outfile=args.OUTFILE,
    min_replicates=args.MIN_REPLICATES,
)
